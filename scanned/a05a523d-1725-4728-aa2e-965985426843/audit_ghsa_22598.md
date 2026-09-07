# [M] Airbnb Knowledge Repo XSS In Comments

## Summary
Severity: Medium
Advisory: GHSA-xmw7-848p-p95w
CVE: CVE-2018-12104
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-xmw7-848p-p95w
Type: github-advisory

## Affected
- PyPI: `knowledge-repo` — affected >=0 <0.9.0

## Details
Cross-site scripting (XSS) vulnerability in Airbnb Knowledge Repo prior to 0.9.0 allows remote attackers to inject arbitrary web scripts or HTML via the post comments functionality, as demonstrated by the `post/posts/new_report.kp` URI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12104
- https://github.com/airbnb/knowledge-repo/issues/254
- https://github.com/airbnb/knowledge-repo/issues/431
- https://github.com/airbnb/knowledge-repo/pull/558
- https://github.com/airbnb/knowledge-repo/commit/f026ad2afea14e0ffc91f1aa0eaedcdc72c63167
- https://github.com/airbnb/knowledge-repo
- https://github.com/pypa/advisory-database/tree/main/vulns/knowledge-repo/PYSEC-2018-116.yaml
- https://pypi.org/project/knowledge-repo
- https://web.archive.org/web/20200227121013/http://www.securityfocus.com/bid/104487
