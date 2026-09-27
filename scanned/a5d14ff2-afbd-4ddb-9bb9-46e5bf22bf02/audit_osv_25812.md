# [M] Password of talk conversations can be bruteforced in Nextcloud

## Summary
Severity: Medium
Advisory: CVE-2023-45149
Aliases: GHSA-7rf8-pqmj-rpqv
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-10-16
Source: https://osv.dev/vulnerability/CVE-2023-45149
Type: osv

## Details
Nextcloud talk is a chat module for the Nextcloud server platform. In affected versions brute force protection of public talk conversation passwords can be bypassed, as there was an endpoint validating the conversation password without registering bruteforce attempts. It is recommended that the Nextcloud Talk app is upgraded to 15.0.8, 16.0.6 or 17.1.1. There are no known workarounds for this vulnerability.

## References
- https://hackerone.com/reports/2094473
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45149.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-7rf8-pqmj-rpqv
- https://nvd.nist.gov/vuln/detail/CVE-2023-45149
- https://github.com/nextcloud/spreed/pull/10545
