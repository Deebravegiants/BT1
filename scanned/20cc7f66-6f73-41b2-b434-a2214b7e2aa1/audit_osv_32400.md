# [M] CVE-2025-29490

## Summary
Severity: Medium
Advisory: CVE-2025-29490
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2025-29490
Type: osv

## Details
libming v0.4.8 was discovered to contain a segmentation fault via the decompileCALLMETHOD function. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted SWF file.

## References
- https://github.com/goodmow/PoC/blob/main/libming/libming-fuzz8.readme
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/29xxx/CVE-2025-29490.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-29490
- https://github.com/libming/libming/issues/330
