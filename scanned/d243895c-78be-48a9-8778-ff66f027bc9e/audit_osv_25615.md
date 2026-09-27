# [H] Unsalted passwords in fobybus/social-media-skeleton

## Summary
Severity: High
Advisory: CVE-2023-40173
Aliases: GHSA-rfmv-7m7g-v628
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-08-18
Source: https://osv.dev/vulnerability/CVE-2023-40173
Type: osv

## Details
Social media skeleton is an uncompleted/framework social media project implemented using a php, css ,javascript and html. Prior to version 1.0.5 Social media skeleton did not properly salt passwords leaving user passwords susceptible to cracking should an attacker gain access to hashed passwords. This issue has been addressed in version 1.0.5 and users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40173.json
- https://github.com/fobybus/social-media-skeleton/security/advisories/GHSA-rfmv-7m7g-v628
- https://nvd.nist.gov/vuln/detail/CVE-2023-40173
- https://github.com/fobybus/social-media-skeleton/commit/344d798e82d6cc39844962c6d3cb2560f5907848
- https://github.com/fobybus/social-media-skeleton/commit/df31da44ffed3ea065cbbadc3c8052d0d489a2ef
