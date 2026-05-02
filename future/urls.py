# from django.urls import path
# from .views import (
#     CreateQueueView,
#     MyQueueView,
#     QueueListView,
#     NextQueueView
# )
#
# urlpatterns = [
#     path('queue/', CreateQueueView.as_view()),
#     path('queue/my/', MyQueueView.as_view()),
#     path('queue/list/', QueueListView.as_view()),
#     path('queue/next/', NextQueueView.as_view()),
# ]

from django.urls import path
from .views import (
    LoginView,
    RegisterView,
    BranchListView,
    ServiceListView,
    CreateQueueView,
    MyQueueView,
    QueueListView,
    NextQueueView,
    CancelQueueView
)

urlpatterns = [
    # Auth
    path('auth/login/', LoginView.as_view()),
    path('auth/register/', RegisterView.as_view()),

    # Ma'lumotlar
    path('branches/', BranchListView.as_view()),
    path('services/', ServiceListView.as_view()),

    # Navbat operatsiyalari
    path('queue/', CreateQueueView.as_view()),  # POST - navbat olish
    path('queue/my/', MyQueueView.as_view()),  # GET - o'z navbatlari
    path('queue/list/', QueueListView.as_view()),  # GET - barcha navbatlar
    path('queue/next/', NextQueueView.as_view()),  # POST - keyingisini chaqirish
    path('queue/cancel/', CancelQueueView.as_view()),  # POST - navbatni bekor qilish
]
