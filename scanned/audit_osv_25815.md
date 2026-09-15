# [M] OAuth2 client_secret stored in plain text in the Nextcloud database

## Summary
Severity: Medium
Advisory: CVE-2023-45151
Aliases: GHSA-hhgv-jcg9-p4m9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-10-16
Source: https://osv.dev/vulnerability/CVE-2023-45151
Type: osv

## Details
Nextcloud server is an open source home cloud platform. Affected versions of Nextcloud stored OAuth2 tokens in plaintext which allows an attacker who has gained access to the server to potentially elevate their privilege. This issue has been addressed and users are recommended to upgrade their Nextcloud Server to version 25.0.8, 26.0.3 or 27.0.1. There are no known workarounds for this vulnerability.

## References
- https://hackerone.com/reports/1994324
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45151.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-hhgv-jcg9-p4m9
- https://nvd.nist.gov/vuln/detail/CVE-2023-45151
- https://github.com/nextcloud/server/pull/38398
