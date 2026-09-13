# [H] Pimcore Unrestricted Upload of File with Dangerous Type

## Summary
Severity: High
Advisory: GHSA-cxj7-4jpj-2q38
CVE: CVE-2019-16318
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cxj7-4jpj-2q38
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <5.7.1

## Details
In Pimcore before 5.7.1, an attacker with limited privileges can bypass file-extension restrictions via a 256-character filename, as demonstrated by the failure of automatic renaming of .php to .php.txt for long filenames, a different vulnerability than CVE-2019-10867 and CVE-2019-16317.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16318
- https://github.com/pimcore/pimcore/commit/732f1647cc6e0a29b5b1f5d904b4d726b5e9455f
- https://github.com/pimcore/pimcore
- https://snyk.io/vuln/SNYK-PHP-PIMCOREPIMCORE-451598
