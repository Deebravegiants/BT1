# [M] CVE-2024-41437

## Summary
Severity: Medium
Advisory: CVE-2024-41437
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-41437
Type: osv

## Details
A heap buffer overflow in the function cp_unfilter() (/vendor/cute_png.h) of hicolor v0.5.0 allows attackers to cause a Denial of Service (DoS) via a crafted PNG file.

## References
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/heapof-r1-cp_unfilter-cute_png-1019c11/poc/sample6.png
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/heapof-r1-cp_unfilter-cute_png-1019c11/vulDescription.assets/image-20240530183857985.png
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/heapof-r1-cp_unfilter-cute_png-1019c11/vulDescription.md
- https://github.com/Helson-S/FuzzyTesting/tree/master/hicolor/heapof-r1-cp_unfilter-cute_png-1019c11
- https://github.com/Helson-S/FuzzyTesting/tree/master/hicolor/heapof-r1-cp_unfilter-cute_png-1019c11/poc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41437.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41437
