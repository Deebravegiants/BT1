# [C] SQL Injection in WordPress Zero Spam WordPress plugin

## Summary
Severity: Critical
Advisory: GHSA-pq2f-3fg3-rw99
CVE: CVE-2022-0254
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-15
Source: https://github.com/advisories/GHSA-pq2f-3fg3-rw99
Type: github-advisory

## Affected
- Packagist: `bmarshall511/wordpress_zero_spam` — affected >=0 <5.2.13

## Details
The WordPress Zero Spam WordPress plugin before 5.2.13 does not properly sanitise and escape the order and orderby parameters before using them in a SQL statement in the admin dashboard, leading to a SQL injection

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0254
- https://github.com/Highfivery/zero-spam-for-wordpress/commit/49723f696f1e2f2a76ac89375910bb036a4895f3
- https://github.com/Highfivery/zero-spam-for-wordpress
- https://plugins.trac.wordpress.org/changeset/2660225
- https://plugins.trac.wordpress.org/changeset/2680906
- https://wpscan.com/vulnerability/ae54681f-7b89-408c-b0ee-ba4a520db997
