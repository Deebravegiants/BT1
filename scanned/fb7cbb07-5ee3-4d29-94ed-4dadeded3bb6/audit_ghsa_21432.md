# [H] LIEF heap buffer overflow in the LIEF::MachO::BinaryParser::parse_dyldinfo_generic_bind

## Summary
Severity: High
Advisory: GHSA-jvp9-phwp-p738
CVE: CVE-2022-43171
CWE: CWE-122, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-18
Source: https://github.com/advisories/GHSA-jvp9-phwp-p738
Type: github-advisory

## Affected
- PyPI: `lief` — affected >=0 <0.12.3

## Details
A heap buffer overflow in the LIEF::MachO::BinaryParser::parse_dyldinfo_generic_bind function of LIEF prior to version 0.12.3 allows attackers to cause a Denial of Service (DoS) via a crafted MachO file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43171
- https://github.com/lief-project/LIEF/issues/782
- https://github.com/lief-project/LIEF
- https://github.com/pypa/advisory-database/tree/main/vulns/lief/PYSEC-2022-43140.yaml
