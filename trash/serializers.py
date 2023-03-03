from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from .models import Trash


class TrashSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    content_type = serializers.CharField()
    
    class Meta:
        model = Trash
        fields = '__all__'
        validators = []

    # def validate(self, data):
    #     if not data['org'].staff_set.filter(user=data['user']).exists():
    #         raise serializers.ValidationError('不属于该组织成员')
    #     return data
        

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        type_str = data.get('content_type')
        try:
            type_list = type_str.split('.')
            content_type = ContentType.objects.get(
                app_label=type_list[0],
                model=type_list[1]
            )
        except Exception as e:
            raise serializers.ValidationError({'content_type': str(e)})

        return {**data, 'content_type': content_type}
        

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.content_type.app_label == 'questions' \
                and instance.content_type.model == 'question':
            from questions.serializers import QuestionSerializer
            ret['content'] = QuestionSerializer(instance.content_object).data

        return ret
