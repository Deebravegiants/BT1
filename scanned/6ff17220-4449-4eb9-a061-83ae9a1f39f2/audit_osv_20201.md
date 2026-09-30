# [M] CVE-2021-32137

## Summary
Severity: Medium
Advisory: CVE-2021-32137
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-13
Source: https://osv.dev/vulnerability/CVE-2021-32137
Type: osv

## Details
Heap buffer overflow in the URL_GetProtocolType function in MP4Box in GPAC 1.0.1 allows attackers to cause a denial of service or execute arbitrary code via a crafted file.

## References
- https://github.com/gpac/gpac/commit/328def7d3b93847d64ecb6e9e0399684e57c3eca
- https://github.com/gpac/gpac/issues/1766
