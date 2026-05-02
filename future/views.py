from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Queue, Service
from .serializers import QueueSerializer, QueueCreateSerializer


# 🔹 Navbat olish
class CreateQueueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QueueCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        queue = serializer.save()

        return Response(QueueSerializer(queue).data)


# 🔹 O‘z navbatini ko‘rish
class MyQueueView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queues = Queue.objects.filter(user=request.user).order_by('-created_at')
        return Response(QueueSerializer(queues, many=True).data)


# 🔹 Admin uchun barcha navbatlar
class QueueListView(APIView):
    def get(self, request):
        queues = Queue.objects.all().order_by('number')
        return Response(QueueSerializer(queues, many=True).data)


# 🔹 Keyingi odamni chaqirish
class NextQueueView(APIView):
    def post(self, request):
        # oldingi active ni done qilish
        active = Queue.objects.filter(status='active').first()
        if active:
            active.status = 'done'
            active.save()

        # yangi active tanlash
        next_queue = Queue.objects.filter(status='waiting').order_by('number').first()

        if next_queue:
            next_queue.status = 'active'
            next_queue.save()
            return Response({
                "message": "Next user called",
                "data": QueueSerializer(next_queue).data
            })

        return Response({"message": "Queue is empty"})
