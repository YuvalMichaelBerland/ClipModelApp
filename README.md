# Smart Images

## Overview
Smart Images is a web application leveraging advanced AI models to simplify the process of searching for specific images among personal media collections. In today's digital world, where vast amounts of media are stored on personal devices, finding a particular image has become a real challenge. Our application harnesses the power of state-of-the-art AI to streamline this search process.

## Project Goals
Our goal was to integrate modern web development—including backend, frontend, and databases—with deep learning technologies to create a seamless and intelligent image search tool. We aimed to mimic the development process of a startup, building an initial yet functional product that demonstrates how AI can effectively solve real-world problems.

## Development Process
- **Exploration Phase**: We researched various web development frameworks and AI models to determine the most suitable technologies for our needs.
- **Convergence Phase**: We selected **Django** as our web framework due to its Python-based ecosystem, which we had extensively used during our studies, particularly in deep learning applications.
- **Model Selection**: We chose **OpenAI's CLIP model**, a discriminative AI model trained on 400 million images and their textual descriptions, enabling it to understand the relationship between images and text effectively.

## Technology Stack
- **Backend**: Django (Python-based framework)
- **Frontend**: Web-based user interface
- **Database**: To manage uploaded images and queries
- **AI Model**: OpenAI CLIP for image-text matching

## How It Works
Smart Images allows users to:
- 📂 Upload images to a centralized platform
- 🔍 Search for specific images using natural language text queries
- 🖼️ Retrieve the most relevant images based on AI-driven matching

Unlike conventional image categorization methods, our application enables users to find images in a way similar to describing them to another person.

## Installation & Usage
### Prerequisites
- Python 3.8+
- Django
- OpenAI API access

### Installation
```bash
# Clone the repository
git clone https://github.com/your-repo/ClipModelApp.git
cd ClipModelApp

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use 'venv\Scripts\activate'

# Install dependencies
pip install -r requirements.txt

# Run the Django server
python manage.py runserver
```

### Usage
1. Upload images via the web interface.
2. Enter a textual description of the image you are searching for.
3. The system retrieves and displays the most relevant images.

## Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request.

## License
This project is licensed under the MIT License.

---

*This project was developed as part of the final year graduation project in the Digital Sciences for High-Tech program at Tel Aviv University.*



https://drive.google.com/file/d/1K3KOe-X09Yyg8EMtyD7KZuzicFqqGEWM/view?usp=sharing 
