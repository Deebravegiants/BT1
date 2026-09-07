# [H] rdiffweb allows unlimited length of root directory name, which could result in DoS

## Summary
Severity: High
Advisory: GHSA-hrj7-f62f-j7x7
CVE: CVE-2022-3295
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-27
Source: https://github.com/advisories/GHSA-hrj7-f62f-j7x7
Type: github-advisory

## Affected
- PyPI: `rdiffweb` — affected >=0 <2.4.8

## Details
rdiffweb prior to 2.4.8 has no limit in length of root directory names. Allowing users to enter long strings may result in a DOS attack or memory corruption. Version 2.4.8 defines a field limit for username, email, and root directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3295
- https://github.com/ikus060/rdiffweb/commit/667657c6fe2b336c90be37f37fb92f65df4feee3
- https://github.com/ikus060/rdiffweb
- https://github.com/pypa/advisory-database/tree/main/vulns/rdiffweb/PYSEC-2022-293.yaml
- https://huntr.dev/bounties/202dd03a-3d97-4c64-bc73-1a0f36614233
