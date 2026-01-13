## How to Run

Download the following files:

* `underpass_detection.py`
* `underpass_detection_main.py`
* `test_export.json`

Run the script as follows:

```bash
python3 underpass_detection_main.py data/test_export_1.json --eps 20
```

### Input Arguments

The script takes two input arguments:

1. **Input file**
   : A CityJSON file to be processed.

2. **Epsilon threshold (`--eps`)**
   : The minimum difference between roof and ground areas required to identify an underpass.
   *(Default: `1e-8`)*

### Outputs
1. **A list of City Object IDs with Underpasses**: Printed to the terminal.
2. **under_obj_eps_*(eps value)*.wkt**: WKT output containing merged roof and ground geometries and area differences for City Objects with underpasses. Load into QGIS for visualization.

The followings are for code verification.

3. **A list of City Object IDs that have only roof surfaces and no ground surfaces**: Printed to the terminal.
4. **ground_pre_union.wkt**: WKT output containing non-merged ground geometries.
5. **roof_pre_union.wkt**: WKT output containing non-merged roof geometries.
6. **ground_union.wkt**: WKT output containing merged ground geometries for each City Object.
7. **roof_union.wkt**: WKT output containing merged roof geometries for each City Object.


## Test result 
Following images are from a test run.

* Area of Interest: Near the Rotterdam central library [(Google Map)](https://maps.app.goo.gl/Jbf8kTrSAJ9F8WbVA)
* eps: 1e-8

<img width="848" height="600" alt="underpass_obj" src="https://github.com/user-attachments/assets/4faf1b73-fab4-44e5-95dc-0526bd6e1a23" />

### <case 1> [(Google Map)](https://maps.app.goo.gl/fj1DfkWNB2VPPi8dA)
<table>
  <tr>
    <td align="left">
      <img alt="Roof and ground surfaces"
           src="https://github.com/user-attachments/assets/ac6337af-9fc2-4be2-84d5-edf6571cd62f"
           height="300">
    </td>
    <td align="left">
      <img alt="Detected underpasses"
           src="https://github.com/user-attachments/assets/e07739ec-31b9-445c-9bc7-8ed06be2e692"
           height="300">
    </td>
  </tr>
</table>

### <case 2> [(Google Map)](https://maps.app.goo.gl/aMC8U6ts1g64jLgf7)
<table>
  <tr>
    <td align="left">
      <img alt="Screenshot 2026-01-08 at 4 02 48 PM" src="https://github.com/user-attachments/assets/e1793df4-64cb-4114-b181-03c37f5d1892"
           height="300">
    </td>
    <td align="left">
      <img alt="Screenshot 2026-01-08 at 4 03 17 PM" src="https://github.com/user-attachments/assets/b4793cce-95c1-4303-a5f1-a4fa018a6be8"
           height="300">
    </td>
  </tr>
</table>

### <case 3> [(Google Map)](https://maps.app.goo.gl/tzY4z9fz2f74AwyN9)
<table>
  <tr>
    <td align="left">
      <img alt="Screenshot 2026-01-08 at 4 05 21 PM" src="https://github.com/user-attachments/assets/294d973b-0a29-4186-ab57-5333c17edf03"
           height="300">
    </td>
    <td align="left">
      <img alt="Screenshot 2026-01-08 at 4 05 13 PM" src="https://github.com/user-attachments/assets/ad58ca1f-0807-422a-ae98-44dc390dc012"
           height="300">
    </td>
  </tr>
</table>

### <case 4> [(Google Map)](https://maps.app.goo.gl/GvFp22FT1pKx5NcW7)
<table>
  <tr>
    <td align="left">
      <img alt="Screenshot 2026-01-08 at 4 06 23 PM" src="https://github.com/user-attachments/assets/9094f465-fb7f-4d79-b3df-ec988ef7142c"
           height="300">
    </td>
    <td align="left">
      <img alt="Screenshot 2026-01-08 at 4 07 00 PM" src="https://github.com/user-attachments/assets/201b2571-906b-4a2d-b4d8-fda6c810ea75"
           height="300">
    </td>
  </tr>
</table>

