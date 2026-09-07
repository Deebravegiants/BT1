# [H] HTTP response splitting in uvicorn

## Summary
Severity: High
Advisory: GHSA-f97h-2pfx-f59f
CVE: CVE-2020-7695
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-07-29
Source: https://github.com/advisories/GHSA-f97h-2pfx-f59f
Type: github-advisory

## Affected
- PyPI: `uvicorn` — affected >=0 <0.11.7

## Details
Uvicorn before 0.11.7 is vulnerable to HTTP response splitting. CRLF sequences are not escaped in the value of HTTP headers. Attackers can exploit exploit this to add arbitrary headers to HTTP responses, or even return an arbitrary response body, whenever crafted input is used to construct HTTP headers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7695
- https://github.com/encode/uvicorn
- https://github.com/pypa/advisory-database/tree/main/vulns/uvicorn/PYSEC-2020-151.yaml
- https://snyk.io/vuln/SNYK-PYTHON-UVICORN-570471
