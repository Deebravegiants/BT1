# [C] Nextcloud global site selector authentication bypass

## Summary
Severity: Critical
Advisory: CVE-2024-22212
Aliases: GHSA-vj5q-f63m-wp77
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2024-01-18
Source: https://osv.dev/vulnerability/CVE-2024-22212
Type: osv

## Details
Nextcloud Global Site Selector is a tool which allows you to run multiple small Nextcloud instances and redirect users to the right server. A problem in the password verification method allows an attacker to authenticate as another user. It is recommended that the Nextcloud Global Site Selector is upgraded to version 1.4.1, 2.1.2, 2.3.4 or 2.4.5. There are no known workarounds for this issue.

## References
- https://hackerone.com/reports/2248689
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/22xxx/CVE-2024-22212.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-vj5q-f63m-wp77
- https://nvd.nist.gov/vuln/detail/CVE-2024-22212
- https://github.com/nextcloud/globalsiteselector/commit/ab5da57190d5bbc79079ce4109b6bcccccd893ee
