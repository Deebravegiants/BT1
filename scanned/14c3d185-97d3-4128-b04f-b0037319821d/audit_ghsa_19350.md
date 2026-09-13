# [M] pypickle unsafe deserialization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5qwj-342r-h886
CVE: CVE-2025-5174
CWE: CWE-20, CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-05-26
Source: https://github.com/advisories/GHSA-5qwj-342r-h886
Type: github-advisory

## Affected
- PyPI: `pypickle` — affected >=0 <2.0.0

## Details
A vulnerability was found in erdogant pypickle up to 1.1.5 and classified as problematic. Affected by this issue is the function load of the file pypickle/pypickle.py. The manipulation leads to deserialization. Local access is required to approach this attack. The exploit has been disclosed to the public and may be used. Upgrading to version 2.0.0 is able to address this issue. The patch is identified as 14b4cae704a0bb4eb6723e238f25382d847a1917. It is recommended to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-5174
- https://github.com/erdogant/pypickle/issues/2
- https://github.com/erdogant/pypickle/issues/2#issuecomment-2889146579
- https://github.com/erdogant/pypickle/commit/14b4cae704a0bb4eb6723e238f25382d847a1917
- https://github.com/erdogant/pypickle
- https://github.com/erdogant/pypickle/releases/tag/2.0.0
- https://github.com/pypa/advisory-database/tree/main/vulns/pypickle/PYSEC-2025-45.yaml
- https://vuldb.com/?ctiid.310262
- https://vuldb.com/?id.310262
- https://vuldb.com/?submit.579157
