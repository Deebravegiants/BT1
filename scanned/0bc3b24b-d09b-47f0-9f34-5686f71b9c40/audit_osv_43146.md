# [M] picocms Pico - Host Header Injection Enables Script Source Hijacking

## Summary
Severity: Medium
Advisory: CVE-2026-72574
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72574
Type: osv

## Details
A host header injection vulnerability in picocms/Pico through 2.1.4 allows an unauthenticated remote attacker to control the origin of JavaScript and CSS assets loaded by the default theme. When base_url is unset (the default), Pico::getBaseUrl in lib/Pico.php builds the base URL from unvalidated Host, X-Forwarded-Host, X-Forwarded-Proto, and X-Forwarded-Port request headers.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72574.json
- https://github.com/picocms/Pico
- https://nvd.nist.gov/vuln/detail/CVE-2026-72574
- https://picocms.org
- https://github.com/picocms/Pico/blob/master/lib/Pico.php
