# [M]  rdiffweb's unlimited length Fullname field can lead to DoS

## Summary
Severity: Medium
Advisory: GHSA-fqfg-c577-2vc3
CVE: CVE-2022-3364
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-09-30
Source: https://github.com/advisories/GHSA-fqfg-c577-2vc3
Type: github-advisory

## Affected
- PyPI: `rdiffweb` — affected >=0 <2.5.0a3

## Details
rdiffweb prior to 2.5.0a3 does not validate email length, allowing users to insert an email longer than 255 characters. If a user signs up with an email with a length of 1 million or more characters and logs in, withdraws, or changes their email, the server may cause denial of service due to overload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3364
- https://github.com/ikus060/rdiffweb/commit/b62c479ff6979563c7c23e7182942bc4f460a2c7
- https://github.com/ikus060/rdiffweb
- https://github.com/pypa/advisory-database/tree/main/vulns/rdiffweb/PYSEC-2022-298.yaml
- https://huntr.dev/bounties/e70ad507-1424-463b-bdf1-c4a6fbe6e720
