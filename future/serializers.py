from rest_framework import serializers
from .models import Queue, Service
from django.contrib.auth import get_user_model

User = get_user_model()


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"


class QueueSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = Queue
        fields = "__all__"


class QueueCreateSerializer(serializers.Serializer):
    service_id = serializers.IntegerField()

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        service_id = validated_data['service_id']

        service = Service.objects.get(id=service_id)

        last = Queue.objects.filter(service=service).order_by('-number').first()
        number = last.number + 1 if last else 1

        queue = Queue.objects.create(
            user=user,
            service=service,
            number=number,
            status='waiting'
        )

        return queue