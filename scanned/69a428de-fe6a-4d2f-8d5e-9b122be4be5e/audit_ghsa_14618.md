# [M] Koji Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-g2vg-8hfg-79vj
CVE: CVE-2024-9427
CWE: CWE-116
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-12-24
Source: https://github.com/advisories/GHSA-g2vg-8hfg-79vj
Type: github-advisory

## Affected
- PyPI: `koji` — affected >=1.35.0 <1.35.1
- PyPI: `koji` — affected >=1.34.0 <1.34.3
- PyPI: `koji` — affected >=0 <1.33.2

## Details
A vulnerability in Koji was found. An unsanitized input allows for an XSS attack. Javascript code from a malicious link could be reflected in the resulting web page. It is not expected to be able to submit an action or make a change in Koji due to existing XSS protections in the code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9427
- https://access.redhat.com/security/cve/CVE-2024-9427
- https://bugzilla.redhat.com/show_bug.cgi?id=2316047
- https://docs.pagure.org/koji/CVEs/CVE-2024-9427
- https://pagure.io/koji
- https://pagure.io/koji/c/8c72d90d7bb991f8fb193851b80847ac9e9474a4?branch=master
