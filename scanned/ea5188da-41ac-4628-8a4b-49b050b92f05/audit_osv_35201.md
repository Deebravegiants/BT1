# [M] ImageMagick converting a malicious MVG file to SVG caused an integer overflow.

## Summary
Severity: Medium
Advisory: CVE-2025-69204
Aliases: GHSA-hrh7-j8q2-4qcw
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2025-69204
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to version 7.1.2-12, in the WriteSVGImage function, using an int variable to store number_attributes caused an integer overflow. This, in turn, triggered a buffer overflow and caused a DoS attack. Version 7.1.2-12 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69204.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-hrh7-j8q2-4qcw
- https://nvd.nist.gov/vuln/detail/CVE-2025-69204
- https://github.com/ImageMagick/ImageMagick/commit/2c08c2311693759153c9aa99a6b2dcb5f985681e
