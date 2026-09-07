# [M] Pallets Werkzeug cross-site scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-h2fp-xgx6-xh6f
CVE: CVE-2016-10516
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-h2fp-xgx6-xh6f
Type: github-advisory

## Affected
- PyPI: `Werkzeug` — affected >=0 <0.11.11

## Details
Cross-site scripting (XSS) vulnerability in the render_full function in debug/tbtools.py in the debugger in Pallets Werkzeug before 0.11.11 (as used in Pallets Flask and other products) allows remote attackers to inject arbitrary web script or HTML via a field that contains an exception message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10516
- https://github.com/pallets/werkzeug/pull/1001
- https://github.com/pallets/werkzeug/commit/1034edc7f901dd645ec6e462754111b39002bd65
- https://github.com/advisories/GHSA-h2fp-xgx6-xh6f
- https://github.com/pallets/werkzeug
- https://github.com/pypa/advisory-database/tree/main/vulns/werkzeug/PYSEC-2017-43.yaml
- https://lists.debian.org/debian-lts-announce/2017/11/msg00037.html
- http://blog.neargle.com/2016/09/21/flask-src-review-get-a-xss-from-debuger
