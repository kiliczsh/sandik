# sandik
oy ve ötesi sitesi üzerinden sandık verilerini toplamak için script


# Install
```console
git clone https://github.com/kiliczsh/sandik.git
cd sandik
python -m venv .venv
pip install - requirements.txt
```

# Run
```console
# To get city, district, neighborhood and school list

python main.py
Enter city plate: 69
# 69 is the plate of Bayburt
# Check sample/BAYBURT.json for sample output

# To get results of a school

python tutanak.py
python tutanak.py
Enter school id: 184742
# 184742 is the id of the school
# Check sample/school_184742.json for sample output
```

# To get bulk results
```console
python bulk_tutanak.py
Enter city json path: ANTALYA.json
# In this case, results will be written to data/7/school_{30535, 30529, 30540, ...}.json
```

# Notes
`SLEEP_TIME = 1` in `main.py` and `tutanak.py` is the sleep time between requests. You can change it if you want.


# Contribution
Feel free to contribute ☘️
