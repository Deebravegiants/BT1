# [H] Pallets Werkzeug Insufficient Entropy

## Summary
Severity: High
Advisory: GHSA-gq9m-qvpx-68hc
CVE: CVE-2019-14806
CWE: CWE-331
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-08-21
Source: https://github.com/advisories/GHSA-gq9m-qvpx-68hc
Type: github-advisory

## Affected
- PyPI: `werkzeug` — affected >=0 <0.15.3

## Details
Pallets Werkzeug before 0.15.3, when used with Docker, has insufficient debugger PIN randomness because Docker containers share the same machine id.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14806
- https://github.com/pallets/werkzeug/commit/00bc43b1672e662e5e3b8cecd79e67fc968fa246
- https://github.com/pallets/werkzeug
- https://github.com/pallets/werkzeug/blob/7fef41b120327d3912fbe12fb64f1951496fcf3e/src/werkzeug/debug/__init__.py#L168
- https://github.com/pypa/advisory-database/tree/main/vulns/werkzeug/PYSEC-2019-140.yaml
- https://palletsprojects.com/blog/werkzeug-0-15-3-released
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00034.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00047.html
