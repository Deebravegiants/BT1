# [M] Cross-site scripting in recommender-xblock

## Summary
Severity: Medium
Advisory: GHSA-3j5x-7ccf-ppgm
CVE: CVE-2018-20858
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-08-21
Source: https://github.com/advisories/GHSA-3j5x-7ccf-ppgm
Type: github-advisory

## Affected
- PyPI: `recommender-xblock` — affected >=0 <1.3.1

## Details
Recommender before 1.3.1 allows XSS. It is possible for a learner to craft a fake resource to recommender, that includes script which could possibly steal credentials from staff if they are lured into viewing the recommended resource.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20858
- https://github.com/edx/RecommenderXBlock/pull/2
- https://github.com/advisories/GHSA-3j5x-7ccf-ppgm
- https://github.com/openedx/RecommenderXBlock
- https://github.com/pypa/advisory-database/tree/main/vulns/recommender-xblock/PYSEC-2019-219.yaml
- https://groups.google.com/forum/#!topic/openedx-announce/SF8Sn6MuUTg
