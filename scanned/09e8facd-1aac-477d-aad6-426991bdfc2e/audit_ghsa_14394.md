# [M] Pimcore vulnerable to improper quoting of filters in Custom Reports

## Summary
Severity: Medium
Advisory: GHSA-vf7q-g2pv-jxvx
CVE: CVE-2023-28438
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-22
Source: https://github.com/advisories/GHSA-vf7q-g2pv-jxvx
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.19

## Details
### Impact
Since a user with 'report' permission can already write arbitrary SQL queries and given the fact that this endpoint is using the GET method (no CSRF protection), an attacker can inject an arbitrary query by manipulating a user to click on a link.

The impact of this path traversal and arbitrary extension is limited (creation of arbitrary files and
appending data to existing files) but when combined with the SQL Injection, the exported data can be controlled and a webshell can be uploaded. Attackers can use that to execute arbitrary PHP code on the server with the permissions of the webserver.

### Patches
Update to version 10.5.19 or apply these patch manually https://github.com/pimcore/pimcore/commit/d1abadb181c88ebaa4bce1916f9077469d4ea2bc.patch
https://github.com/pimcore/pimcore/commit/7f788fa44bc18bc1c9182c25e26b770a1d30b62f.patch

### Workarounds
Apply patches manually:
https://github.com/pimcore/pimcore/commit/d1abadb181c88ebaa4bce1916f9077469d4ea2bc.patch
https://github.com/pimcore/pimcore/commit/7f788fa44bc18bc1c9182c25e26b770a1d30b62f.patch

### References
#14526
#14498

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-vf7q-g2pv-jxvx
- https://nvd.nist.gov/vuln/detail/CVE-2023-28438
- https://github.com/pimcore/pimcore/pull/14526
- https://github.com/pimcore/pimcore/commit/d1abadb181c88ebaa4bce1916f9077469d4ea2bc.patch
- https://github.com/pimcore/pimcore
