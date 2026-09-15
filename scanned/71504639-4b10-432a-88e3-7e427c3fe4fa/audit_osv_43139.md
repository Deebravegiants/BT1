# [M] Ladybird Web Solution Faveo Helpdesk - Broken Access Control

## Summary
Severity: Medium
Advisory: CVE-2026-72554
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72554
Type: osv

## Details
A broken access control vulnerability in Ladybird Web Solution Faveo Helpdesk 2.0.3 allows any self-registered customer to read ticket conversations belonging to other customers via the v1 REST API. The API verifies the existence of the requested ticket but not ownership, enabling any authenticated user to access arbitrary ticket threads including internal agent notes containing sensitive information.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72554.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72554
- https://github.com/ladybirdweb/faveo-helpdesk
