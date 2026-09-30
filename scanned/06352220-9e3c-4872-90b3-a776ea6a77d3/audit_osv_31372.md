# [C] exelban stats XPC Service shouldAcceptNewConnection command injection

## Summary
Severity: Critical
Advisory: CVE-2025-0396
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-01-12
Source: https://osv.dev/vulnerability/CVE-2025-0396
Type: osv

## Details
A vulnerability, which was classified as critical, has been found in exelban stats up to 2.11.21. This issue affects the function shouldAcceptNewConnection of the component XPC Service. The manipulation leads to command injection. It is possible to launch the attack on the local host. Upgrading to version 2.11.22 is able to address this issue. It is recommended to upgrade the affected component.

## References
- https://winslow1984.com/books/cve-collection/page/stats-v21122-local-privilege-escalation
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/0xxx/CVE-2025-0396.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-0396
- https://vuldb.com/?id.291269
- https://vuldb.com/?submit.473229
- https://vuldb.com/?ctiid.291269
- https://github.com/exelban/stats/releases/tag/v2.11.22
