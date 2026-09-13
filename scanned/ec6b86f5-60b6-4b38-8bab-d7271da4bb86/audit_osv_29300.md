# [M] CVE-2024-41438

## Summary
Severity: Medium
Advisory: CVE-2024-41438
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-41438
Type: osv

## Details
A heap buffer overflow in the function cp_stored() (/vendor/cute_png.h) of hicolor v0.5.0 allows attackers to cause a Denial of Service (DoS) via a crafted PNG file.

## References
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/heapof-r65280-cp_stored-cute_png-543c2
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/heapof-r65280-cp_stored-cute_png-543c2/vulDescription.assets/image-20240530184723547.png
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/heapof-r65280-cp_stored-cute_png-543c2/vulDescription.assets/image-20240530184848743.png
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/heapof-r65280-cp_stored-cute_png-543c2/vulDescription.assets/image-20240530185015780.png
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/heapof-r65280-cp_stored-cute_png-543c2/vulDescription.md
- https://github.com/Helson-S/FuzzyTesting/tree/master/hicolor/heapof-r65280-cp_stored-cute_png-543c2/poc
- https://github.com/Helson-S/FuzzyTesting/tree/master/hicolor/heapof-r65280-cp_stored-cute_png-543c2/poc/sample10.png
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41438.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41438
