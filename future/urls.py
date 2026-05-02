from django.urls import path
from .views import (
    CreateQueueView,
    MyQueueView,
    QueueListView,
    NextQueueView
)

urlpatterns = [
    path('queue/', CreateQueueView.as_view()),
    path('queue/my/', MyQueueView.as_view()),
    path('queue/list/', QueueListView.as_view()),
    path('queue/next/', NextQueueView.as_view()),
]