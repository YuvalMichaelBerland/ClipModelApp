#from django.db import models
import torch
#import os
#from PIL import Image
from transformers import CLIPTokenizerFast, CLIPProcessor, CLIPModel
from .models import Photo
import json
import numpy as np


class ClipModel:
    def __init__(self, model_id="openai/clip-vit-base-patch32", images= []):
    # initialize the CLIP pre-trained model, and empty images list
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = CLIPTokenizerFast.from_pretrained(model_id)
        self.processor = CLIPProcessor.from_pretrained(model_id)
        self.model = CLIPModel.from_pretrained(model_id).to(self.device)
        self.images = images


    def process_single_image(self, image):
    # append the image to images list + return the image's model vector using extract_vectors_images func
        self.images.append(image)
        my_img_vector = self.extract_vectors_images(image)
        return my_img_vector


    def extract_vectors_text(self, text_prompts):
    # return the model vector for a single image
        text_inputs = self.tokenizer(text_prompts, padding=True, return_tensors="pt")
        text_features = self.model.get_text_features(**text_inputs)
        return text_features


    def extract_vectors_images(self, image_list):
    # return the model vector for a single image
        image_inputs = self.processor(images=image_list, return_tensors="pt")
        image_features = self.model.get_image_features(**image_inputs)
        return image_features


    def extract_image_vectors_from_db(self,user):
        image_vectors_dict = {}
        photos = Photo.objects.filter(user=user)

        for photo in photos:
            if photo.vector is not None and photo.vector: # check that there is vector
                vector_dict = json.loads(photo.vector) #decode the vector from JSON
                vector_np = np.asarray(vector_dict["array"]) # convert it back to numpy array
                vector = torch.tensor(vector_np)  # Convert the numpy array vector to a tensor
                image_vectors_dict[photo.id] = (vector, photo.image.url)  # Save the vector and the image URL

        return image_vectors_dict


    def similarity_score(self, text_vector, images_vectors):
    # a fun that calc the similarity score between all images and search text
        # Convert text_feature to a tensor, if it isn't already
        if not isinstance(text_vector, torch.Tensor):
          text_vector = torch.tensor(text_vector)

        # Prepare a tensor to store the similarity scores
        similarity_scores = torch.zeros(len(images_vectors))

        # Calculate the similarity score with each image feature
        image_urls = []
        image_ids = []
        for i, (image_id, (image_feature, image_url)) in enumerate(images_vectors.items()):
            # Convert image_feature to a tensor, if it isn't already
            if not isinstance(image_feature, torch.Tensor):
                image_feature = torch.tensor(image_feature)

            # Calculate the similarity score and store it
            logit_scale = self.model.logit_scale.exp()
            #similarity = torch.nn.functional.cosine_similarity(text_vector.unsqueeze(0),image_feature.unsqueeze(0)) * logit_scale
            similarity = torch.nn.functional.cosine_similarity(text_vector, image_feature) * logit_scale
            similarity_scores[i] = similarity

            # Store the image ID and URL
            image_ids.append(image_id)
            image_urls.append(image_url)

        # Compute the index of the image with the highest score
        max_index = torch.argmax(similarity_scores).item()

        # newwwww Compute the indices of the top 3 images with the highest scores
        top_indices = torch.argsort(similarity_scores, descending=True)[:5]
        top_image_ids = [image_ids[idx] for idx in top_indices]

        # Return the tensor of scores, the id and url of the image with the highest score, and the highest score
        return similarity_scores, image_ids[max_index], image_urls, similarity_scores[max_index], top_image_ids, image_ids


    def classify_category (self, categories, image):
    # check with clip model what is the best category for the image
        inputs = self.processor(text=categories, images=image, return_tensors="pt", padding=True)
        outputs = self.model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)
        top_index = torch.argmax(probs)
        category = categories[top_index]
        return category