# [M] All users can reset the allowed apps list for Nextcloud Guest App users

## Summary
Severity: Medium
Advisory: CVE-2024-22401
Aliases: GHSA-wr87-hx3w-29hh
CVSS: 4.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:N/A:N)
Published: 2024-01-18
Source: https://osv.dev/vulnerability/CVE-2024-22401
Type: osv

## Details
Nextcloud guests app is a utility to create guest users which can only see files shared with them. In affected versions users could change the allowed list of apps, allowing them to use apps that were not intended to be used. It is recommended that the Guests app is upgraded to 2.4.1, 2.5.1 or 3.0.1. There are no known workarounds for this vulnerability.

## References
- https://hackerone.com/reports/2250398
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/22xxx/CVE-2024-22401.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-wr87-hx3w-29hh
- https://nvd.nist.gov/vuln/detail/CVE-2024-22401
- https://github.com/nextcloud/guests/pull/1082
