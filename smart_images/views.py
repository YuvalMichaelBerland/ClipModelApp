from django.shortcuts import render, redirect, get_object_or_404
from .classModel import *
from .jsonencoder import *
from PIL import Image
import json
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Photo
from django.shortcuts import render, redirect, get_object_or_404
from .models import Photo, Category
from django.http import Http404


def home(request):
    # home page
    return render(request, 'smart_images/home.html')


@login_required
def gallery(request):
    # gallery page
    category = request.GET.get('category')
    if category is None:
        photos = Photo.objects.filter(user=request.user)
    else:
        photos = Photo.objects.filter(user=request.user, category__name=category)
    categories = Category.objects.all()
    context = {'categories': categories, 'photos': photos}
    return render(request, 'smart_images/gallery.html', context)


@login_required
def view_photo(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    user_categories = Category.objects.filter(user=request.user)
    default_categories = Category.objects.filter(user=None)
    all_categories = user_categories | default_categories

    if request.method == 'POST':
        new_category_id = request.POST.get('new_category')
        if new_category_id:
            new_category = get_object_or_404(Category, pk=new_category_id)
            photo.category = new_category
            photo.save()
            return redirect('smart-images-gallery')  # Redirect to gallery page after updating category

    context = {'photo': photo, 'all_categories': all_categories}
    return render(request, 'smart_images/viewphoto.html', context)


@login_required
def view_multiple_photos(request, pk):
    # view photo page
    image_ids = pk.split(',')  # Split the comma-separated IDs into a list
    photos = Photo.objects.filter(id__in=image_ids, user=request.user)  # Fetch the photos using the IDs
    return render(request, 'smart_images/gallery.html', {'photos': photos})


@login_required
def delete_photo(request, pk):
    photo = get_object_or_404(Photo, pk=pk)

    # Check if the photo belongs to the current user
    if photo.user != request.user:
        raise Http404("This photo does not exist or you don't have permission to delete it.")

    if request.method == 'POST':
        photo.delete()

    return redirect('smart-images-gallery')  # Redirect to gallery page after deleting photo


@login_required
# upload new images page
def upload_images(request):
    clip_model = ClipModel() # create an instance of the clip model

    user_categories = Category.objects.filter(user=request.user)
    default_categories = Category.objects.filter(user=None)
    categories_list = list(user_categories.values_list('name', flat=True)) + list(default_categories.values_list('name', flat=True))
    context = {'user_categories': user_categories, 'default_categories': default_categories}
    if request.method == 'POST':
        data = request.POST
        images = request.FILES.getlist('image')
        description = data.get('description', '')  # Get the description from the form

        for image in images:
            pil_image = Image.open(image)  # Opening the image using PIL
            chosen_category = clip_model.classify_category(categories_list,pil_image)
                #print("After classify_category call")
                #print(chosen_category)
            category = Category.objects.get(name=chosen_category)

            #  extract image features for future search
            single_image_vector = clip_model.process_single_image(pil_image) # Processing the image with clip model (return image vector)
            single_image_vector_np = single_image_vector.detach().numpy()  # Convert Tensor to NumPy array
            single_image_vector_dict = {"array": single_image_vector_np} # put the numpy array in dict in order to use json
            single_image_vector_json = json.dumps(single_image_vector_dict, cls=NumpyArrayEncoder) #encode the vector to json

            #  check if the image name already exsist
            if Photo.objects.filter(image__iexact=image.name).exists():
                messages.error(request, 'Image with the same name already exists.')
                return redirect('smart-images-upload-images')


            #  create new object of type photo in DB
            photo = Photo.objects.create(user=request.user,category=category, image=image,  description=description, vector=single_image_vector_json)

        return redirect('smart-images-gallery')
    return render(request, 'smart_images/upload.html', context)




@login_required
def search_images(request):
    clip_model = ClipModel()  # create an instance of the clip model
    if request.method == 'POST':
        query = request.POST.get('query', '')  # Extract the value of the 'query' input field (the search text)
        text_vector = clip_model.extract_vectors_text(query)  # Processing the text with clip model (return text vector)
        images_vectors_dict = clip_model.extract_image_vectors_from_db(
            user=request.user)  # take all the existing vectors for the current user from the DB

        similarity_scores, best_image_id, image_urls, _, top_image_ids, image_ids = clip_model.similarity_score(
            text_vector, images_vectors_dict)  # calc the similarity scores and return the image id of the best image

        if "images" in query.lower() or "photos" in query.lower():
            best_images_ids = []
            th = 0.5
            for i in range(0, 5):
                probs = similarity_scores.softmax(dim=0)
                max_index = probs.argmax()  # Find the index of the maximum value
                max_value = probs[max_index]  # Get the maximum value
                if max_value >= th:  # check if the prob is greater than or equal to the threshold
                    th = th + 0.1
                    similarity_scores = torch.cat((similarity_scores[:max_index], similarity_scores[max_index + 1:]))
                    best_images_ids.append(image_ids[max_index])
                    image_ids.pop(max_index)
                else:
                    break

            if not best_images_ids:
                #message = "There is no image that strongly matches your search."
                messages.error(request, 'There is no image that strongly matches your search.')
                return redirect('smart-images-gallery')
                #return render(request, 'smart_images/gallery.html', {'message': message})

            return redirect('smart-images-view-multiple-photos', pk=','.join(map(str, best_images_ids)))
        else:
            th = 0.8
            probs = similarity_scores.softmax(dim=0)
            max_index = probs.argmax()  # Find the index of the maximum value
            max_value = probs[max_index]  # Get the maximum value
            if max_value >= th:  # check if the prob is greater than or equal to the threshold
                return redirect('smart-images-view-photo', pk=best_image_id)
            else:
                messages.error(request, 'There is no image that strongly matches your search.')
                return redirect('smart-images-gallery')
                #message = "There is no image that strongly matches your search."
                #return render(request, 'smart_images/gallery.html', {'message': message})
    return render(request, 'smart_images/gallery.html')


@login_required
def edit_categories(request):
    user_categories = Category.objects.filter(user=request.user)
    default_categories = Category.objects.filter(user=None)
    context = {'user_categories': user_categories, 'default_categories': default_categories}
    return render(request, 'smart_images/editcategories.html', context)


@login_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        user = request.user
        Category.objects.create(user=user, name=name)
        return redirect('smart-images-edit-categories')
    return render(request, 'smart_images/add_category.html')


@login_required
def delete_category(request):
    user_categories = Category.objects.filter(user=request.user)

    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        Category.objects.filter(name=category_name, user=request.user).delete()
        return redirect('smart-images-edit-categories')

    context = {'user_categories': user_categories}
    return render(request, 'smart_images/delete_category.html', context)


@login_required
def edit_category(request):
    user_categories = Category.objects.filter(user=request.user)

    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        new_name = request.POST.get('new_name')
        category = Category.objects.get(name=category_name, user=request.user)
        category.name = new_name
        category.save()
        return redirect('smart-images-edit-categories')

    context = {'user_categories': user_categories}
    return render(request, 'smart_images/edit_category.html', context)


@login_required
def auto_categories_update(request):
    clip_model = ClipModel()  # create an instance of the clip model

    user_categories = Category.objects.filter(user=request.user)
    default_categories = Category.objects.filter(user=None)

    # Create a list of category names for both user's and default categories
    categories_list = list(user_categories.values_list('name', flat=True)) + list(
        default_categories.values_list('name', flat=True))

    no_category_photos = Photo.objects.filter(user=request.user, category=None)

    # classify image to one of the categories
    for photo in no_category_photos:
        pil_image = Image.open(photo.image.path)
        chosen_category = clip_model.classify_category(categories_list, pil_image)

        # Get the category object based on the chosen category name
        if chosen_category in user_categories.values_list('name', flat=True):
            category = user_categories.get(name=chosen_category)
        else:
            category = default_categories.get(name=chosen_category)

        photo.category = category
        photo.save()

    return redirect('smart-images-gallery')
