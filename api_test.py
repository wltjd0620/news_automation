import google.generativeai as genai

genai.configure(api_key=gemini_api_key)

for model in genai.list_models():
    print('Model: {model_name}'.format(model_name=model.name))
    for method in model.supported_generation_methods:
        print('- {method}'.format(method=method))