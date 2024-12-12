from datetime import datetime

def footer_context(request):
    return {'year': datetime.now().year}
