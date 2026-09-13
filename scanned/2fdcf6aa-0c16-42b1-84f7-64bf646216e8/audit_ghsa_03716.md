# [C] Recurly vulnerable to SSRF

## Summary
Severity: Critical
Advisory: GHSA-38rv-5jqc-m2cv
CVE: CVE-2017-0906
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-01-04
Source: https://github.com/advisories/GHSA-38rv-5jqc-m2cv
Type: github-advisory

## Affected
- PyPI: `recurly` — affected >=2.6.0 <2.6.2
- PyPI: `recurly` — affected >=2.5.0 <2.5.1
- PyPI: `recurly` — affected >=2.4.0 <2.4.5
- PyPI: `recurly` — affected >=2.3.0 <2.3.1
- PyPI: `recurly` — affected >=2.2.0 <2.2.22
- PyPI: `recurly` — affected >=2.1.0 <2.1.16
- PyPI: `recurly` — affected >=0 <2.0.5

## Details
The Recurly Client Python Library before 2.0.5, 2.1.16, 2.2.22, 2.3.1, 2.4.5, 2.5.1, 2.6.2 is vulnerable to a Server-Side Request Forgery vulnerability in the `Resource.get` method that could result in compromise of API keys or other critical resources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-0906
- https://github.com/recurly/recurly-client-python/commit/049c74699ce93cf126feff06d632ea63fba36742
- https://hackerone.com/reports/288635
- https://dev.recurly.com/page/python-updates
- https://github.com/advisories/GHSA-38rv-5jqc-m2cv
- https://github.com/pypa/advisory-database/tree/main/vulns/recurly/PYSEC-2017-68.yaml
