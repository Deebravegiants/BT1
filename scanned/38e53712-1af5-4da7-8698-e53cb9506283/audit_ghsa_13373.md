# [C] xalpha vulnerable to Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-jx3q-5rgf-vrrr
CVE: CVE-2023-37659
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-11
Source: https://github.com/advisories/GHSA-jx3q-5rgf-vrrr
Type: github-advisory

## Affected
- PyPI: `xalpha` — affected >=0.11.4 <0.11.9

## Details
xalpha v0.11.4 is vulnerable to Remote Command Execution (RCE). User input is not properly checked to be numerical values prior to being evaluated.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37659
- https://github.com/refraction-ray/xalpha/issues/175
- https://github.com/refraction-ray/xalpha/commit/6dceaa159a1a319d750ade20a4595956876657b6
- https://github.com/pypa/advisory-database/tree/main/vulns/xalpha/PYSEC-2023-116.yaml
- https://github.com/refraction-ray/xalpha
