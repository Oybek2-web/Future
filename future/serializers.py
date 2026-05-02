# from rest_framework import serializers
# from .models import Queue, Service
# from django.contrib.auth import get_user_model
#
# User = get_user_model()
#
#
# class ServiceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Service
#         fields = '__all__'
#
#
# class QueueSerializer(serializers.ModelSerializer):
#     user = serializers.StringRelatedField(read_only=True)
#     service = ServiceSerializer(read_only=True)
#
#     class Meta:
#         model = Queue
#         fields = "__all__"
#
#
# class QueueCreateSerializer(serializers.Serializer):
#     service_id = serializers.IntegerField()
#
#     def create(self, validated_data):
#         request = self.context['request']
#         user = request.user
#         service_id = validated_data['service_id']
#
#         service = Service.objects.get(id=service_id)
#
#         last = Queue.objects.filter(service=service).order_by('-number').first()
#         number = last.number + 1 if last else 1
#
#         queue = Queue.objects.create(
#             user=user,
#             service=service,
#             number=number,
#             status='waiting'
#         )
#
#         return queue

from rest_framework import serializers
from .models import Queue, Service, Branch
from django.contrib.auth import get_user_model

User = get_user_model()


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name', 'address']


class ServiceSerializer(serializers.ModelSerializer):
    branch = BranchSerializer(read_only=True)
    branch_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Service
        fields = ['id', 'name', 'duration', 'branch', 'branch_id']


class QueueSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    service = ServiceSerializer(read_only=True)
    branch = BranchSerializer(read_only=True)

    class Meta:
        model = Queue
        fields = '__all__'
        read_only_fields = ['number', 'status', 'created_at', 'started_at', 'finished_at']


class QueueCreateSerializer(serializers.Serializer):
    service_id = serializers.IntegerField(min_value=1)
    branch_id = serializers.IntegerField(min_value=1)  # ✅ Yangi qo'shildi

    def validate_service_id(self, value):
        if not Service.objects.filter(id=value).exists():
            raise serializers.ValidationError('Bunday xizmat topilmadi')
        return value

    def validate_branch_id(self, value):
        if not Branch.objects.filter(id=value).exists():
            raise serializers.ValidationError('Bunday filial topilmadi')
        return value

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        service_id = validated_data['service_id']
        branch_id = validated_data['branch_id']

        service = Service.objects.select_related('branch').get(id=service_id)

        # ✅ Filial mosligini tekshirish
        if service.branch_id != branch_id:
            raise serializers.ValidationError('Bu xizmat tanlangan filialda mavjud emas')

        # ✅ Thread-safe raqam olish
        number = Queue.get_next_number(service, service.branch)

        queue = Queue.objects.create(
            user=user,
            service=service,
            branch=service.branch,  # service.branch orqali olamiz
            number=number,
            status='waiting'
        )
        return queue