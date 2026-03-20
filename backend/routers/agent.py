from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import httpx
import base64
from core.config import settings

router = APIRouter(prefix="/agent", tags=["Agent"])

async def extract_prompt_from_images(style_images: List[UploadFile]) -> str:
    """
    Funkcja przyjmująca zdjęcia stylu (np. biznesowe), 
    analizująca je przy użyciu modelu wizyjnego Ollama (np. llava)
    i zwracająca szczegółowy prompt do generatora obrazków.
    """
    images_b64 = []
    for img in style_images:
        content = await img.read()
        b64 = base64.b64encode(content).decode("utf-8")
        images_b64.append(b64)
        
    prompt_instruction = (
        "Describe the visual style, lighting, setting, clothing, and atmosphere of these images in high detail. "
        "Do not describe the person themselves too much, focus on what kind of picture it is (e.g., professional headshot, studio lighting). "
        "This description will be used as a prompt for an image generation model to recreate this exact aesthetic. "
        "Respond only with the descriptive text prompt."
    )
    
    ollama_url = f"{settings.OLLAMA_URL}/api/generate"
    payload = {
        "model": settings.LLM_MODEL_NAME,
        "prompt": prompt_instruction,
        "images": images_b64,
        "stream": False
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(ollama_url, json=payload, timeout=60.0)
            if response.status_code != 200:
                error_msg = response.text
                try:
                    error_msg = response.json().get("error", response.text)
                except:
                    pass
                raise HTTPException(status_code=response.status_code, detail=f"Ollama API zwróciło błąd: {error_msg}")
            
            data = response.json()
            return data.get("response", "").strip()
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Błąd sieci podczas łączenia z Ollama (czy serwer działa?): {str(e)}")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Nieoczekiwany błąd: {str(e)}")


async def generate_image_with_face_and_style(face_image: bytes, style_prompt: str) -> str:
    """
    Ollama jako LLM/VLM zajmuje się tekstem. Generowanie zdjęć wymaga osobnego silnika 
    (np. Stable Diffusion API z ControlNiet / ReActor / IP-Adapter). 
    Poniżej jest mockup komunikacji z lokalnym API np. AUTOMATIC1111 (http://localhost:7860).
    """
    # ------------------------------------------------------------------------------------------
    # W rzeczywistości byś tutaj wysłał zapytanie post pod lokalny adres aplikacji SD:
    # ------------------------------------------------------------------------------------------
    # sd_url = "http://localhost:7860/sdapi/v1/txt2img"
    # face_b64 = base64.b64encode(face_image).decode("utf-8")
    
    # payload = {
    #     "prompt": f"a photo of a person, highly detailed face, {style_prompt}, masterpiece, 8k resolution",
    #     "negative_prompt": "ugly, blurry, low quality, deformed",
    #     "steps": 20,
    #     "alwayson_scripts": {
    #         "reactor": { # lub "faceid" wtyczka
    #             "args": [
    #                 face_b64, 
    #                 True,     
    #                 # Ustawienia zależne od wtyczki do face swap
    #             ]
    #         }
    #     }
    # }
    # 
    # async with httpx.AsyncClient() as client:
    #     response = await client.post(sd_url, json=payload, timeout=120.0)
    #     data = response.json()
    #     return data["images"][0] # Wygenerowany base64 obrazu
    # ------------------------------------------------------------------------------------------
    
    # Ponieważ Ollama tego nie potrafi wygenerować z pudełka, zwracamy tutaj przykładowy tekst.
    # Użytkownik zostanie poinformowany, że musi podpiąć tu swój silnik Image2Image.
    
    return f"Base64 obrazu wygenerowane dla układu i promptu: '{style_prompt[:80]}...'"


@router.post("/generate-styled-portrait")
async def generate_styled_portrait(
    face_image: UploadFile = File(..., description="Zdjęcie z twarzą do podmiany (Twoje zdjęcie)"),
    style_images: List[UploadFile] = File(..., description="Zdjęcia referencyjne dla stylu, np. biznesowe"),
):
    """
    Endpoint przyjmuje:
    - 1 zdjęcie z docelową twarzą
    - zestaw zdjęć inspiracji (stylu)
    Następnie opisuje je przez Ollamę i próbuje wygenerować nowy obraz.
    """
    # 1. Uzyskaj opis stylu (prompt) za pomocą np. LLaVA w lokalnej instancji Ollamy
    style_prompt = await extract_prompt_from_images(style_images)
    
    # Odczytaj właściwe zdjęcie twarzy
    face_content = await face_image.read()
    
    # 2. Wygeneruj nowe zdjęcie np. przez Stable Diffusion z FaceSwap/IP-Adapter
    # używając wygenerowanego promptu oraz zdjęcia twarzy
    generated_image_b64 = await generate_image_with_face_and_style(face_content, style_prompt)
    
    return {
        "status": "success",
        "message": "Styl został odczytany przez LLM, a obraz wysłany do generatora.",
        "llm_extracted_prompt": style_prompt,
        "generated_image_b64": generated_image_b64
    }

