from db_utilities import DbUtiltity

class Brand:
    def __init__(self, p_brand_name='', p_models=[]):
        self.name = p_brand_name
        self.models = p_models
    
    def serialize(self):
        return {
            'name': self.name,
            'models': self.models
        }

def get_all_brands():
    _brands = []
    tmp_dict = {}
    with DbUtiltity() as db_util:

        result = db_util.find_all_brands()
        for rec in result:
            brand_name = rec['brand']
            model_name = rec['model']

            if brand_name in tmp_dict:
                tmp_dict[brand_name].append(model_name)
            else:
                tmp_dict[brand_name] = [model_name]
        
        _brands = [Brand(key, tmp_dict.get(key)) for key in tmp_dict]
        
    return _brands

def get_models_by_brand(brand_name):
    _models = []

    with DbUtiltity() as db_util:
        result = db_util.find_models_by_brand(brand_name)
        for rec in result:
            _models.append(rec['model'])
    
    return _models

def add_model_to_brand(brand, model):
    with DbUtiltity() as db_util:
        db_util.save_brand_model({"brand":brand, "model":model})
