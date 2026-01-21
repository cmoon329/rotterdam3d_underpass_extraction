## How to Run

Download the following files:

* `underpass_detection.py`
* `underpass_detection_main.py`
* Test datasets in `/data` folder

Run the script as follows:

```bash
python3 underpass_detection_main.py data/area_1.json area_1_underpass
```

### Input Arguments

The script takes two input arguments:

1. **Input file**
   : A CityJSON file to be processed
2. **Output file name**
   : An output file name without extension

### Outputs
1. **SHP file**: A SHP file will be created in `/data` folder. The file contains merged Outer Ceiling Surfaces and their area for each City Object with underpasses. Load into QGIS for visualization.

### Test datasets
* `area_1.json`: Near Rotterdam central library [(Google Maps)](https://maps.app.goo.gl/Jbf8kTrSAJ9F8WbVA)
* `area_2.json`: Near Maritime Museum [(Google Maps)](https://maps.app.goo.gl/m2ZSWcXNRb1PzAwg7)
* `area_3.json`: Near Rotterdam central station [(Google Maps)](https://maps.app.goo.gl/LYL9RUEJYVvBS7YD9)

### Notes
**Generic attributes** must be included in the input dataset.
Be sure to include them when downloading a new dataset from 3D Rotterdam.

<img width="250" alt="Screenshot 2026-01-21 at 9 31 31 PM" src="https://github.com/user-attachments/assets/9ca2ee0a-6fa4-4455-8a2f-074819e57645" />


## Results
Following images are from test runs.
**Surfaces highlighted in green** represent **underpass** surfaces.
| Area 1 | Area 2 | Area 3 |
|----------|----------|----------|
| <img width="400" alt="area_1_map" src="https://github.com/user-attachments/assets/f109b592-ec55-4e1a-b20b-96fd68c79d77" /> | <img width="400" alt="area_2_map" src="https://github.com/user-attachments/assets/14bb8b39-2cdc-47e3-8a52-e8af37b83de1" /> | <img width="400" alt="area_3_map" src="https://github.com/user-attachments/assets/30ebb328-948b-480d-9437-54583440c937" /> |

**Example 1** [(Google Map)](https://maps.app.goo.gl/fj1DfkWNB2VPPi8dA)
<table>
  <tr>
    <td align="left">
      <img alt="Roof and ground surfaces"
           src="https://github.com/user-attachments/assets/83165c5e-14e6-4f96-be29-ba59285e3f0b"
           height="300">
    </td>
    <td align="left">
      <img alt="Detected underpasses"
           src="https://github.com/user-attachments/assets/e07739ec-31b9-445c-9bc7-8ed06be2e692"
           height="300">
    </td>
  </tr>
</table>

**Example 2** [(Google Map)](https://maps.app.goo.gl/aMC8U6ts1g64jLgf7)
<table>
  <tr>
    <td align="left">
      <img alt="Screenshot 2026-01-08 at 4 02 48 PM" src="https://github.com/user-attachments/assets/4f7b6c98-5506-44e8-9ab2-f3deed0a69c5"
           height="300">
    </td>
    <td align="left">
      <img alt="Screenshot 2026-01-08 at 4 03 17 PM" src="https://github.com/user-attachments/assets/b4793cce-95c1-4303-a5f1-a4fa018a6be8"
           height="300">
    </td>
  </tr>
</table>

**Example 3** [(Google Map)](https://maps.app.goo.gl/tzY4z9fz2f74AwyN9)
<table>
  <tr>
    <td align="left">
      <img alt="Screenshot 2026-01-08 at 4 05 21 PM" src="https://github.com/user-attachments/assets/fb40d6d1-8a79-40c6-b361-a35a852dd893"
           height="300">
    </td>
    <td align="left">
      <img alt="Screenshot 2026-01-08 at 4 05 13 PM" src="https://github.com/user-attachments/assets/ad58ca1f-0807-422a-ae98-44dc390dc012"
           height="300">
    </td>
  </tr>
</table>

**Example 4** [(Google Map)](https://maps.app.goo.gl/GvFp22FT1pKx5NcW7)
<table>
  <tr>
    <td align="left">
      <img alt="Screenshot 2026-01-08 at 4 06 23 PM" src="https://github.com/user-attachments/assets/0efd85a1-cdb5-4616-95f9-ab9bcaa492e1"
           height="300">
    </td>
    <td align="left">
      <img alt="Screenshot 2026-01-08 at 4 07 00 PM" src="https://github.com/user-attachments/assets/201b2571-906b-4a2d-b4d8-fda6c810ea75"
           height="300">
    </td>
  </tr>
</table>
