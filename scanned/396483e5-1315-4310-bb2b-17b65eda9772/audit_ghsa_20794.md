# [M] rdiffweb vulnerable to password complexity bypass leading to weak passwords

## Summary
Severity: Medium
Advisory: GHSA-8wxf-c45w-g66g
CVE: CVE-2022-3326
CWE: CWE-521
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-30
Source: https://github.com/advisories/GHSA-8wxf-c45w-g66g
Type: github-advisory

## Affected
- PyPI: `rdiffweb` — affected >=0 <2.4.9

## Details
ikus060/rdiffweb prior to 2.4.9 allows a user to set there password to all spaces. While rdiffweb has a password policy requiring passwords to be between 8 and 128 characters, it does not validate the password entropy, allowing users to bypass password complexity requirements with weak passwords. This issue has been fixed in version 2.4.9. No workarounds are known to exist.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3326
- https://github.com/ikus060/rdiffweb/commit/ee98e5af78ec60db8a17fef6ea0ca250e3f31eec
- https://github.com/ikus060/rdiffweb
- https://github.com/pypa/advisory-database/tree/main/vulns/rdiffweb/PYSEC-2022-297.yaml
- https://huntr.dev/bounties/1f6a5e49-23f2-45f7-8661-19f9cee8ae97
