# [M] Improper handling of request URLs in Nextcloud Guests app allows guest users to bypass app allowlist

## Summary
Severity: Medium
Advisory: CVE-2024-22402
Aliases: GHSA-v3qw-7vgv-2fxj
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-01-18
Source: https://osv.dev/vulnerability/CVE-2024-22402
Type: osv

## Details
Nextcloud guests app is a utility to create guest users which can only see files shared with them. In affected versions users were able to load the first page of apps they were actually not allowed to access. Depending on the selection of apps installed this may present a permissions bypass. It is recommended that the Guests app is upgraded to 2.4.1, 2.5.1 or 3.0.1. There are no known workarounds for this vulnerability.

## References
- https://hackerone.com/reports/2251074
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/22xxx/CVE-2024-22402.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-v3qw-7vgv-2fxj
- https://nvd.nist.gov/vuln/detail/CVE-2024-22402
- https://github.com/nextcloud/guests/pull/1082
