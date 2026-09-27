# [M] CVE-2024-41440

## Summary
Severity: Medium
Advisory: CVE-2024-41440
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-41440
Type: osv

## Details
A heap buffer overflow in the function png_quantize() of hicolor v0.5.0 allows attackers to cause a Denial of Service (DoS) via a crafted PNG file.

## References
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/heapof-w1-png_quantize-cli-220c32
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/heapof-w1-png_quantize-cli-220c32/poc
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/heapof-w1-png_quantize-cli-220c32/poc/sample18.png
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/heapof-w1-png_quantize-cli-220c32/vulDescription.assets/image-20240530225208577.png
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/heapof-w1-png_quantize-cli-220c32/vulDescription.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41440.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41440
