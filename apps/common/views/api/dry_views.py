from django.http import HttpResponse
from apps.common.views.api import AppAPIView
from apps.city.models import City
import csv

class ArchiveAPIView(AppAPIView):
    """Archive view for all models which require only a model name"""
    
    def post(self, request):
        MODEL_CHOICES = {
            "city": City,
        }
        print(request.data.get("type"))

        if request.data.get("type") is None:
            return self.send_error_response()
        model = MODEL_CHOICES[request.data.get("type")]
        try:
            if model == City:
                City.objects.filter(id__in=request.data.get("id_list")).delete()
                return self.send_response()
            else:
                return self.send_error_response()
        except:
            return self.send_error_response()
        
def export_common_csv(request, columns, model=None, data_for_export: list[list] = None):
    """
    Common function for all the other export views. Contains common
    and other dry functions for other views.
    """

    assert not model or not data_for_export  # checking

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="file.csv"'

    writer = csv.writer(response)

    writer.writerow(columns)

    if model:
        # Checking given is model or QuerySet
        query_set = model.objects if hasattr(model, "objects") else model
        for _object in query_set.all().values_list(*columns):
            writer.writerow(_object)

    if data_for_export:
        for _data in data_for_export:
            writer.writerow(_data)

    return response