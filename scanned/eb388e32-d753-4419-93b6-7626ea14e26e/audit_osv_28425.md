# [C] Masa CMS Vulnerable to Pre-Auth RCE via JSON API

## Summary
Severity: Critical
Advisory: CVE-2024-32641
Aliases: GHSA-cj9g-v5mq-qrjm
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-03
Source: https://osv.dev/vulnerability/CVE-2024-32641
Type: osv

## Details
Masa CMS is an open source Enterprise Content Management platform. Masa CMS versions prior to 7.2.8, 7.3.13, and 7.4.6 are vulnerable to remote code execution. The vulnerability exists in the addParam function, which accepts user input via the criteria parameter. This input is subsequently evaluated by setDynamicContent, allowing an unauthenticated attacker to execute arbitrary code via the m tag. The vulnerability is patched in versions 7.2.8, 7.3.13, and 7.4.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32641.json
- https://github.com/MasaCMS/MasaCMS/security/advisories/GHSA-cj9g-v5mq-qrjm
- https://nvd.nist.gov/vuln/detail/CVE-2024-32641
- https://github.com/MasaCMS/MasaCMS/commit/fb27f822fe426496af71205fa35208e58823fcf6
