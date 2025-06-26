import io
from PIL import Image
import pytest
from vit_server import app

# test_vit_server.py


@pytest.fixture
def client():
    """Fixture to set up the Flask test client."""
    with app.test_client() as client:
        yield client

def test_predict_valid_image(client):
    """Test the predict endpoint with a valid image."""
    # Create a dummy image
    image = Image.new('RGB', (224, 224), color='white')
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='JPEG')
    image_bytes.seek(0)

    # Send POST request with the image
    response = client.post('/predict', data={'image': (image_bytes, 'test.jpg')})
    assert response.status_code == 200
    assert 'prediction' in response.get_json()

def test_predict_no_image(client):
    """Test the predict endpoint without sending an image."""
    response = client.post('/predict', data={})
    assert response.status_code == 400
    assert response.get_json() == {'error': 'No image file'}

def test_predict_invalid_image(client):
    """Test the predict endpoint with an invalid image."""
    invalid_image = io.BytesIO(b'not an image')
    response = client.post('/predict', data={'image': (invalid_image, 'test.jpg')})
    assert response.status_code == 500
    assert 'error' in response.get_json()