# [H] Basic auth header on WebDAV requests is not brute-force protected in Nextcloud

## Summary
Severity: High
Advisory: CVE-2023-32319
Aliases: GHSA-mr7q-xf62-fw54
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-05-26
Source: https://osv.dev/vulnerability/CVE-2023-32319
Type: osv

## Details
Nextcloud server is an open source personal cloud implementation. Missing brute-force protection on the WebDAV endpoints via the basic auth header allowed to brute-force user credentials when the provided user name was not an email address. Users from version 24.0.0 onward are affected. This issue has been addressed in releases 24.0.11, 25.0.5 and 26.0.0. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32319.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-mr7q-xf62-fw54
- https://nvd.nist.gov/vuln/detail/CVE-2023-32319
- https://github.com/nextcloud/server/pull/37227
