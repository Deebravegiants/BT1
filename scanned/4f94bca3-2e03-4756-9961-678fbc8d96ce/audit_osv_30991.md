# [M] CVE-2024-57435

## Summary
Severity: Medium
Advisory: CVE-2024-57435
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-31
Source: https://osv.dev/vulnerability/CVE-2024-57435
Type: osv

## Details
In macrozheng mall-tiny 1.0.1, an attacker can send null data through the resource creation interface resulting in a null pointer dereference occurring in all subsequent operations that require authentication, which triggers a denial-of-service attack and service restart failure.

## References
- https://github.com/peccc/restful_vul/blob/main/mall_tiny_dos/mall_tiny_dos.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57435.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57435
