from django.core.management.base import BaseCommand, CommandError
from ansible_modules.utils.module_manager import moduledocs
from ansible_modules.models import AnsibleModule
from ansible_modules.forms import AnsibleModuleForm, AnsibleModuleOptionForm
from django.forms.models import model_to_dict

class Command(BaseCommand):
    help = 'Loads anisble modules into the database.'
    
    def _models_to_list_dicts(self, model_list):
        for model in model_list:
            yield model_to_dict(model)

    def handle(self, *args, **kwargs):
        installed_modules = self._models_to_list_dicts(AnsibleModule.objects.all())
        imported_modules = moduledocs.get_all_module_docs()

        def installed(module_path):
            for installed_module in installed_modules:
                if module_path == installed_module['module_path']: 
                    return True
                else:
                    continue
            return False

        for imported_module in imported_modules:
            full_module_path = imported_module['module_path']
            if installed(full_module_path):
                continue
            else:
                form = AnsibleModuleForm(imported_module)
                if form.is_valid():
                    module_instance = form.save()
                    for option in imported_module['options']:
                        option['module'] = module_instance.id
                        option_form = AnsibleModuleOptionForm(option)
                        if option_form.is_valid():
                            option_form.save()
                else:
                    print "Module %s did not load. Form was invalid!" % full_module_path
                    print "ERROR: %s" % form.errors

