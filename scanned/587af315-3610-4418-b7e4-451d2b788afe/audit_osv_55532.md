# [M] CVE-2025-65803

## Summary
Severity: Medium
Advisory: CVE-2025-65803
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-12-10
Source: https://osv.dev/vulnerability/CVE-2025-65803
Type: osv

## Details
An integer overflow in the psdParser::ReadImageData function of FreeImage v3.18.0 and before allows attackers to cause a Denial of Service (DoS) via supplying a crafted PSD file.

## References
- https://freeimage.sourceforge.io/download.html
- https://gist.github.com/1mxml/cabd6d972557d9d992fe5f4f6ca1dd87
