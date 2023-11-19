import os
import re
from openpilot.common.basedir import BASEDIR
from openpilot.common.params import Params

BRAND_MAPPING = {
  "Acura": "Honda",
  "Audi": "Volkswagen",
  "Buick": "GM",
  "Cadillac": "GM",
  "Chevrolet": "GM",
  "Genesis": "Hyundai",
  "GMC": "GM",
  "Jeep": "Chrysler",
  "Kia": "Hyundai",
  "Lexus": "Toyota",
  "Lincoln": "Ford",
  "MAN": "Volkswagen",
  "Ram": "Chrysler",
  "SEAT": "Volkswagen",
  "Škoda": "Volkswagen"
}

class CAR_REGEX:
  CLASS_DEFINITION = re.compile(r'class CAR\(StrEnum\):([\s\S]*?)(?=^\w)', re.MULTILINE)
  CAR_NAMES = re.compile(r'=\s*"([^"]+)"')

def get_names(dir_path, brand=None):
  items = {"names": []}
  brand_lower = (BRAND_MAPPING.get(brand, brand).lower() if brand else None)

  for folder in os.listdir(dir_path):
    brand_name, _, _ = folder.partition('_')
    mapped_brand = BRAND_MAPPING.get(brand_name, brand_name)

    if not brand or mapped_brand.lower() == brand_lower:
      folder_path = os.path.join(dir_path, folder, 'values.py')
      if os.path.exists(folder_path):
        with open(folder_path) as f:
          content = f.read()
        match = CAR_REGEX.CLASS_DEFINITION.search(content)

        if match:
          car_names = CAR_REGEX.CAR_NAMES.findall(match.group(1))
          items["names"].extend(car_names)

  return sorted(items["names"])

def set_params(params, dir_path, param_name, brand=None):
  items = get_names(dir_path, brand)
  params.put(param_name, ','.join(items))

if __name__ == "__main__":
  params = Params()
  dir_path = os.path.join(BASEDIR, 'openpilot', 'selfdrive', 'car')
  brand = params.get("CarBrand", encoding='utf-8')

  set_params(params, dir_path, "CarModels", brand)
