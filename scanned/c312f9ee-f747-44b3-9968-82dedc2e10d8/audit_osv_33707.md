# [M] Dataease Authentication Bypass Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-49001
Aliases: GHSA-xx2m-gmwg-mf3r
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2025-06-03
Source: https://osv.dev/vulnerability/CVE-2025-49001
Type: osv

## Details
DataEase is an open source business intelligence and data visualization tool. Prior to version 2.10.10, secret verification does not take effect successfully, so a user can use any secret to forge a JWT token. The vulnerability has been fixed in v2.10.10. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49001.json
- https://github.com/dataease/dataease/security/advisories/GHSA-xx2m-gmwg-mf3r
- https://nvd.nist.gov/vuln/detail/CVE-2025-49001
