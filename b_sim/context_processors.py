from .forms import CycleForm


def cycle_selection_form(request):
    return {
        'cycle_selection_form': CycleForm(),
    }