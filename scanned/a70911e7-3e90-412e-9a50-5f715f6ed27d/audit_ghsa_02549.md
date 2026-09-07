# [H] OS Command Injection in bikeshed

## Summary
Severity: High
Advisory: GHSA-87cj-px37-rc3x
CVE: CVE-2021-23422
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-87cj-px37-rc3x
Type: github-advisory

## Affected
- PyPI: `bikeshed` — affected >=0 <3.0.0

## Details
This affects the package bikeshed before 3.0.0. This can occur when an untrusted source file containing Inline Tag Command metadata is processed. When an arbitrary OS command is executed, the command output would be included in the HTML output.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23422
- https://github.com/tabatkins/bikeshed/commit/b2f668fca204260b1cad28d5078e93471cb6b2dd
- https://github.com/pypa/advisory-database/tree/main/vulns/bikeshed/PYSEC-2021-116.yaml
- https://github.com/tabatkins/bikeshed
- https://snyk.io/vuln/SNYK-PYTHON-BIKESHED-1537646
