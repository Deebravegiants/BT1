# [M] pypickle Incorrect Privilege Assignment vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qpxx-2cwh-r5vh
CVE: CVE-2025-5175
CWE: CWE-266
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-05-26
Source: https://github.com/advisories/GHSA-qpxx-2cwh-r5vh
Type: github-advisory

## Affected
- PyPI: `pypickle` — affected >=0 <2.0.0

## Details
A vulnerability was found in erdogant pypickle up to 1.1.5. It has been classified as critical. This affects the function Save of the file pypickle/pypickle.py. The manipulation leads to improper authorization. Attacking locally is a requirement. The exploit has been disclosed to the public and may be used. Upgrading to version 2.0.0 is able to address this issue. The patch is named 14b4cae704a0bb4eb6723e238f25382d847a1917. It is recommended to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-5175
- https://github.com/erdogant/pypickle/issues/3
- https://github.com/erdogant/pypickle/issues/3#issue-3070689116
- https://github.com/erdogant/pypickle/issues/3#issuecomment-2888589652
- https://github.com/erdogant/pypickle/commit/14b4cae704a0bb4eb6723e238f25382d847a1917
- https://github.com/PrinceRaj-0/Vulnerability-Disclosure/blob/main/CVE-2025-5175.md
- https://github.com/erdogant/pypickle
- https://github.com/erdogant/pypickle/releases/tag/2.0.0
- https://github.com/pypa/advisory-database/tree/main/vulns/pypickle/PYSEC-2025-46.yaml
- https://vuldb.com/?ctiid.310263
- https://vuldb.com/?id.310263
- https://vuldb.com/?submit.579824
