# [M] Djiblets Cross-site scripting Vulnerability via JSON Objects

## Summary
Severity: Medium
Advisory: GHSA-w7rq-8f2g-jvqr
CVE: CVE-2014-3994
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-w7rq-8f2g-jvqr
Type: github-advisory

## Affected
- PyPI: `Djblets` — affected >=0 <0.7.30
- PyPI: `Djblets` — affected >=0.8 <0.8.3

## Details
A cross-site scripting (XSS) vulnerability in `util/templatetags/djblets_js.py` in Djblets before 0.7.30 and 0.8.x before 0.8.3 for Django, as used in Review Board, allows remote attackers to inject arbitrary web script or HTML via a JSON object, as demonstrated by the name field when changing a user name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3994
- https://github.com/djblets/djblets/commit/50000d0bbb983fa8c097b588d06b64df8df483bd
- https://github.com/djblets/djblets/commit/77a68c03cd619a0996f3f37337b8c39ca6643d6e
- https://github.com/djblets/djblets/commit/e2c79117efd925636acd871a5f473512602243cf
- https://code.google.com/p/reviewboard/issues/detail?id=3406
- https://github.com/djblets/djblets
- https://github.com/pypa/advisory-database/tree/main/vulns/djblets/PYSEC-2014-78.yaml
- https://web.archive.org/web/20140702014704/http://seclists.org/oss-sec/2014/q2/498
- https://web.archive.org/web/20140702025724/http://seclists.org/oss-sec/2014/q2/494
- https://web.archive.org/web/20200228144945/http://www.securityfocus.com/bid/67932
