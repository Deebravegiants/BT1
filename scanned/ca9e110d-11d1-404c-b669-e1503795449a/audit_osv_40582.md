# [M] FreeScout has unrestricted file upload without rate limiting that leads to resource exhaustion (DoS)

## Summary
Severity: Medium
Advisory: CVE-2026-53596
Aliases: GHSA-ph4f-2jhx-q76w
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-53596
Type: osv

## Details
FreeScout is a free help desk and shared inbox built with PHP's Laravel framework. Prior to version 1.8.224, the FreeScout helpdesk application does not enforce rate limiting on the file upload endpoint. Any user can flood the server with upload requests, leading to database overload and potential denial of service for all users. Version 1.8.224 contains a fix.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53596.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-ph4f-2jhx-q76w
- https://nvd.nist.gov/vuln/detail/CVE-2026-53596
