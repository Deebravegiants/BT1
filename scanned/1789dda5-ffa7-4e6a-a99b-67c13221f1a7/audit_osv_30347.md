# [M] CVE-2024-51242

## Summary
Severity: Medium
Advisory: CVE-2024-51242
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-10-30
Source: https://osv.dev/vulnerability/CVE-2024-51242
Type: osv

## Details
A Server-Side Request Forgery (SSRF) vulnerability has been identified in eladmin 2.7 and earlier in ServerDeployController.java. The manipulation of the HTTP Body ip parameter leads to SSRF.

## References
- https://github.com/shadia0/Patienc/blob/main/eladmin_ssrf.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/51xxx/CVE-2024-51242.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-51242
