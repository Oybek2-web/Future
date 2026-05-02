# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from .models import Queue, Service
# from .serializers import QueueSerializer, QueueCreateSerializer
#
#
# # 🔹 Navbat olish
# class CreateQueueView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         serializer = QueueCreateSerializer(data=request.data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         queue = serializer.save()
#
#         return Response(QueueSerializer(queue).data)
#
#
# # 🔹 O‘z navbatini ko‘rish
# class MyQueueView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         queues = Queue.objects.filter(user=request.user).order_by('-created_at')
#         return Response(QueueSerializer(queues, many=True).data)
#
#
# # 🔹 Admin uchun barcha navbatlar
# class QueueListView(APIView):
#     def get(self, request):
#         queues = Queue.objects.all().order_by('number')
#         return Response(QueueSerializer(queues, many=True).data)
#
#
# # 🔹 Keyingi odamni chaqirish
# class NextQueueView(APIView):
#     def post(self, request):
#         # oldingi active ni done qilish
#         active = Queue.objects.filter(status='active').first()
#         if active:
#             active.status = 'done'
#             active.save()
#
#         # yangi active tanlash
#         next_queue = Queue.objects.filter(status='waiting').order_by('number').first()
#
#         if next_queue:
#             next_queue.status = 'active'
#             next_queue.save()
#             return Response({
#                 "message": "Next user called",
#                 "data": QueueSerializer(next_queue).data
#             })
#
#         return Response({"message": "Queue is empty"})

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import Queue, Service, Branch
from .serializers import QueueSerializer, QueueCreateSerializer, ServiceSerializer, BranchSerializer
from django.db import transaction

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test


# 🔹 Login (Token olish)
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username va password kiritilishi shart'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': {'id': user.id, 'username': user.username, 'phone': user.phone}
            })
        return Response({'error': 'Noto\'g\'ri login yoki parol'},
                        status=status.HTTP_401_UNAUTHORIZED)


# 🔹 Ro'yxatdan o'tish
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        username = request.data.get('username')
        password = request.data.get('password')
        phone = request.data.get('phone')

        if not all([username, password, phone]):
            return Response({'error': 'Barcha maydonlar to\'ldirilishi shart'},
                            status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Bu username band'},
                            status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(phone=phone).exists():
            return Response({'error': 'Bu telefon raqam band'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username,
            password=password,
            phone=phone
        )
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': {'id': user.id, 'username': user.username, 'phone': user.phone}
        }, status=status.HTTP_201_CREATED)


# 🔹 Filiallar ro'yxati
class BranchListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        branches = Branch.objects.all()
        serializer = BranchSerializer(branches, many=True)
        return Response(serializer.data)


# 🔹 Xizmatlar ro'yxati (filial bo'yicha)
class ServiceListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        branch_id = request.query_params.get('branch_id')
        if branch_id:
            services = Service.objects.filter(branch_id=branch_id)
        else:
            services = Service.objects.all()
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)


# 🔹 Navbat olish
class CreateQueueView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = QueueCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        queue = serializer.save()
        return Response(QueueSerializer(queue).data, status=status.HTTP_201_CREATED)


# 🔹 O'z navbatlarini ko'rish
class MyQueueView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queues = Queue.objects.filter(user=request.user).order_by('-created_at')
        serializer = QueueSerializer(queues, many=True)
        return Response(serializer.data)


# 🔹 Admin uchun barcha navbatlar (faqat auth)
class QueueListView(APIView):
    permission_classes = [IsAuthenticated]  # ✅ Permission qo'shildi

    def get(self, request):
        branch_id = request.query_params.get('branch_id')
        service_id = request.query_params.get('service_id')
        status_filter = request.query_params.get('status')

        queues = Queue.objects.select_related('user', 'service', 'branch').all()

        if branch_id:
            queues = queues.filter(branch_id=branch_id)
        if service_id:
            queues = queues.filter(service_id=service_id)
        if status_filter:
            queues = queues.filter(status=status_filter)

        queues = queues.order_by('number')
        serializer = QueueSerializer(queues, many=True)
        return Response(serializer.data)


# 🔹 Keyingi odamni chaqirish (faqat admin/operator)
class NextQueueView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        branch_id = request.data.get('branch_id')
        service_id = request.data.get('service_id')

        # ✅ Avvalgi active ni done qilish
        active = Queue.objects.filter(status='active').first()
        if active:
            active.status = 'done'
            active.finished_at = active.__class__._meta.get_field('finished_at').auto_now_add = False
            from django.utils import timezone
            active.finished_at = timezone.now()
            active.save(update_fields=['status', 'finished_at'])

        # ✅ Yangi active tanlash
        filters = {'status': 'waiting'}
        if branch_id:
            filters['branch_id'] = branch_id
        if service_id:
            filters['service_id'] = service_id

        next_queue = Queue.objects.filter(**filters).order_by('number').select_for_update().first()

        if next_queue:
            next_queue.status = 'active'
            from django.utils import timezone
            next_queue.started_at = timezone.now()
            next_queue.save(update_fields=['status', 'started_at'])
            return Response({
                'message': 'Keyingi foydalanuvchi chaqirildi',
                'data': QueueSerializer(next_queue).data
            })

        return Response({'message': 'Navbat bo\'sh'}, status=status.HTTP_204_NO_CONTENT)


# 🔹 Navbatni bekor qilish
class CancelQueueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        queue_id = request.data.get('queue_id')
        try:
            queue = Queue.objects.get(id=queue_id, user=request.user)
            if queue.status == 'waiting':
                queue.status = 'cancelled'
                queue.save(update_fields=['status'])
                return Response({'message': 'Navbat bekor qilindi'})
            return Response({'error': 'Faqat kutayotgan navbatni bekor qilish mumkin'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Queue.DoesNotExist:
            return Response({'error': 'Navbat topilmadi'}, status=status.HTTP_404_NOT_FOUND)



@login_required
def index_view(request):
    return render(request, 'index.html', {
        'branches': Branch.objects.all()
    })

@login_required
def my_queues_view(request):
    return render(request, 'my.html', {
        'branches': Branch.objects.all()
    })

@user_passes_test(lambda u: u.is_staff)
def admin_panel_view(request):
    return render(request, 'admin.html', {
        'branches': Branch.objects.all()
    })