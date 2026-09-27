# [M] CVE-2024-41443

## Summary
Severity: Medium
Advisory: CVE-2024-41443
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-41443
Type: osv

## Details
A stack overflow in the function cp_dynamic() (/vendor/cute_png.h) of hicolor v0.5.0 allows attackers to cause a Denial of Service (DoS) via a crafted PNG file.

## References
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/stkof-w133-cp_dynamic-cute_png-603
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/stkof-w133-cp_dynamic-cute_png-603/poc
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/stkof-w133-cp_dynamic-cute_png-603/poc/sample16.png
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/stkof-w133-cp_dynamic-cute_png-603/vulDescription.assets/image-20240530223831738.png
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/stkof-w133-cp_dynamic-cute_png-603/vulDescription.assets/image-20240530223921086.png
- https://github.com/Helson-S/FuzzyTesting/blob/master/hicolor/stkof-w133-cp_dynamic-cute_png-603/vulDescription.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41443.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41443
