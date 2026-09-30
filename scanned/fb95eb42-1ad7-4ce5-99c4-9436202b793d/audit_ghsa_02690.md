# [H] CSV injection in shuup

## Summary
Severity: High
Advisory: GHSA-663j-rjcr-789f
CVE: CVE-2021-25962
CWE: CWE-1236
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-30
Source: https://github.com/advisories/GHSA-663j-rjcr-789f
Type: github-advisory

## Affected
- PyPI: `shuup` — affected >=0.4.2 <2.11.0

## Details
“Shuup” application in versions 0.4.2 to 2.10.8 is affected by the “Formula Injection” vulnerability. A customer can inject payloads in the name input field in the billing address while buying a product. When a store administrator accesses the reports page to export the data as an Excel file and opens it, the payload gets executed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25962
- https://github.com/shuup/shuup/commit/0a2db392e8518410c282412561461cd8797eea51
- https://github.com/pypa/advisory-database/tree/main/vulns/shuup/PYSEC-2021-355.yaml
- https://github.com/shuup/shuup
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25962
