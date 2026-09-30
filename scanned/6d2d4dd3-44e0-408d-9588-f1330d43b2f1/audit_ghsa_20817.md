# [M] rdiffweb vulnerable to Use of Cache Containing Sensitive Information

## Summary
Severity: Medium
Advisory: GHSA-7fqm-jm52-f9vc
CVE: CVE-2022-3292
CWE: CWE-524
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-29
Source: https://github.com/advisories/GHSA-7fqm-jm52-f9vc
Type: github-advisory

## Affected
- PyPI: `rdiffweb` — affected >=0 <2.4.9

## Details
rdiffweb prior to version 2.4.9 is vulnerable to Use of Cache Containing Sensitive Information. Due to improper cache control, an attacker can view sensitive information even if they are not logged into an account. Version 2.4.9 contains a patch for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3292
- https://github.com/ikus060/rdiffweb/commit/2406780831618405a13113377a784f3102465f40
- https://github.com/ikus060/rdiffweb
- https://github.com/pypa/advisory-database/tree/main/vulns/rdiffweb/PYSEC-2022-296.yaml
- https://huntr.dev/bounties/e9309018-e94f-4e15-b7d1-5d38b6021c5d
