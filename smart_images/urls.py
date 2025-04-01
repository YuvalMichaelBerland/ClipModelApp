from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='smart-images-home'),
    path('upload/', views.upload_images, name='smart-images-upload-images'),
    path('search/', views.search_images, name='smart-images-search-images'),
    path('gallery/', views.gallery, name='smart-images-gallery'),
    path('gallery/<str:pk>/', views.view_photo, name='smart-images-view-photo'),
    path('gallery/multiple/<str:pk>/', views.view_multiple_photos, name='smart-images-view-multiple-photos'),  # Multiple photos view
    path('edit_category/', views.edit_category, name='smart-images-edit-category'),
    path('add_category/', views.add_category, name='smart-images-add-category'),
    path('delete_category/', views.delete_category, name='smart-images-delete-category'),
    path('edit_categories/', views.edit_categories, name='smart-images-edit-categories'),
    path('auto_categories_update/', views.auto_categories_update, name='smart-images-auto-categories-update'),
    path('gallery/<str:pk>/delete/', views.delete_photo, name='smart-images-delete-photo'),
]