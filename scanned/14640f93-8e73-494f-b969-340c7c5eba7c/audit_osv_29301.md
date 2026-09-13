# [M] CVE-2024-41439

## Summary
Severity: Medium
Advisory: CVE-2024-41439
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-41439
Type: osv

## Details
A heap buffer overflow in the function cp_block() (/vendor/cute_png.h) of hicolor v0.5.0 allows attackers to cause a Denial of Service (DoS) via a crafted PNG file.

## References
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/heapof-w98-cp_block-5c0-cute_png-642c5
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/heapof-w98-cp_block-5c0-cute_png-642c5/poc
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/heapof-w98-cp_block-5c0-cute_png-642c5/poc/sample13.png
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/heapof-w98-cp_block-5c0-cute_png-642c5/vulDescription.assets/image-20240530192505615.png
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/heapof-w98-cp_block-5c0-cute_png-642c5/vulDescription.assets/image-20240531002753478.png
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/heapof-w98-cp_block-5c0-cute_png-642c5/vulDescription.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41439.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41439
