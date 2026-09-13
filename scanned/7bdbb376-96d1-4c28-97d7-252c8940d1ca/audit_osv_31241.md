# [H] CVE-2024-6586

## Summary
Severity: High
Advisory: CVE-2024-6586
Aliases: GHSA-4h7x-6vxh-7hjf
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N)
Published: 2024-08-30
Source: https://osv.dev/vulnerability/CVE-2024-6586
Type: osv

## Details
Lightdash version 0.1024.6 allows users with the necessary permissions, such as Administrator or Editor, to create and share dashboards. A dashboard that contains HTML elements which point to a threat actor controlled source can trigger an SSRF request when exported, via a POST request to /api/v1/dashboards//export. The forged request contains the value of the exporting user’s session token. A threat actor could obtain the session token of any user who exports the dashboard. The obtained session token can be used to perform actions as the victim on the application, resulting in session takeover.

## References
- https://github.com/lightdash/lightdash/releases/tag/0.1027.2
- https://patch-diff.githubusercontent.com/raw/lightdash/lightdash/pull/9295.patch
- https://www.cve.org/CVERecord?id=CVE-2024-6586
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6586.json
- https://github.com/google/security-research/security/advisories/GHSA-4h7x-6vxh-7hjf
- https://nvd.nist.gov/vuln/detail/CVE-2024-6586
- https://github.com/lightdash/lightdash/pull/9295
- https://github.com/lightdash/lightdash
