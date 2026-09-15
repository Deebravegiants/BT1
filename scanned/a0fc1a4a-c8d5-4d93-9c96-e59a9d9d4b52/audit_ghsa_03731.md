# [C] modulemd uses an unsafe function for processing externally provided data

## Summary
Severity: Critical
Advisory: GHSA-jhjh-ghwx-6h7r
CVE: CVE-2017-1002157
CWE: CWE-20, CWE-242
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-01-17
Source: https://github.com/advisories/GHSA-jhjh-ghwx-6h7r
Type: github-advisory

## Affected
- PyPI: `modulemd` — affected >=0 <1.3.2

## Details
modulemd 1.3.1 and earlier uses an unsafe function for processing externally provided data, leading to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1002157
- https://github.com/pypa/advisory-database/tree/main/vulns/modulemd/PYSEC-2019-153.yaml
- https://github.com/xsuchy/modulemd
- https://pagure.io/modulemd/issue/55
