# [H] Pyo Buffer Overflow Vulnerability

## Summary
Severity: High
Advisory: GHSA-qj27-32wp-ghrg
CVE: CVE-2021-41498
CWE: CWE-120
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-12-18
Source: https://github.com/advisories/GHSA-qj27-32wp-ghrg
Type: github-advisory

## Affected
- PyPI: `pyo` — affected >=0 <1.0.4

## Details
Buffer overflow in ajaxsoundstudio.com Pyo <= 1.03 in the `Server_jack_init function` which allows attackers to conduct Denial of Service attacks by arbitrary constructing a overlong `client_name`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41498
- https://github.com/belangeo/pyo/issues/221
- https://github.com/belangeo/pyo/commit/017702c73332a8560c8554a36250a6da587a2418
- https://github.com/belangeo/pyo
- https://github.com/pypa/advisory-database/tree/main/vulns/pyo/PYSEC-2021-890.yaml
