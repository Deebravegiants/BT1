# [H] Cross-site Scripting in Pyhtml2pdf

## Summary
Severity: High
Advisory: GHSA-p3rv-qj56-2fqx
CVE: CVE-2024-1647
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-p3rv-qj56-2fqx
Type: github-advisory

## Affected
- PyPI: `pyhtml2pdf` — affected >=0

## Details
Pyhtml2pdf version 0.0.6 allows an external attacker to remotely obtain

arbitrary local files. This is possible because the application does not

validate the HTML content entered by the user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1647
- https://fluidattacks.com/advisories/oliver
- https://github.com/pypa/advisory-database/tree/main/vulns/pyhtml2pdf/PYSEC-2024-301.yaml
- https://pypi.org/project/pyhtml2pdf
