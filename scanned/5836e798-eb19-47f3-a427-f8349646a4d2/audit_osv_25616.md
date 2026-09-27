# [M] Insufficient Session Expiration in fobybus/social-media-skeleton

## Summary
Severity: Medium
Advisory: CVE-2023-40174
Aliases: GHSA-cr5c-ggwq-g4hq
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-08-18
Source: https://osv.dev/vulnerability/CVE-2023-40174
Type: osv

## Details
Social media skeleton is an uncompleted/framework social media project implemented using a php, css ,javascript and html. Insufficient session expiration is a web application security vulnerability that occurs when a web application does not properly manage the lifecycle of a user's session. Social media skeleton releases prior to 1.0.5 did not properly limit manage user session lifecycles. This issue has been addressed in version 1.0.5 and users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40174.json
- https://github.com/fobybus/social-media-skeleton/security/advisories/GHSA-cr5c-ggwq-g4hq
- https://nvd.nist.gov/vuln/detail/CVE-2023-40174
- https://github.com/fobybus/social-media-skeleton/commit/99738b2cc5efb6a5739161c931daa43f99431e5a
