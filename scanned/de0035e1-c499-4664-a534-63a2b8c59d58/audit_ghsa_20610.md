# [C] exotel-py includes code execution backdoor inserted by a third party

## Summary
Severity: Critical
Advisory: GHSA-cv6j-9835-p7fh
CVE: CVE-2022-38792
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-28
Source: https://github.com/advisories/GHSA-cv6j-9835-p7fh
Type: github-advisory

## Affected
- PyPI: `exotel` — affected 0.1.6

## Details
The exotel (aka exotel-py) package in PyPI as of 0.1.6 includes a code execution backdoor inserted by a third party. Users should downgrade to version 0.1.5 to avoid the problem.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38792
- https://github.com/sarathsp06/exotel-py/issues/10
- https://github.com/jertel/elastalert2/pull/931
- https://github.com/pypa/advisory-database/tree/main/vulns/exotel/PYSEC-2022-43134.yaml
- https://github.com/sarathsp06/exotel-py
- https://inspector.pypi.io/project/exotel/0.1.6/packages/8b/ed/9ebeb34d4adb9b01151d73ccfde9c1cb2d629c3b146953c8727559a65446/exotel-0.1.6.tar.gz/exotel-0.1.6/setup.py
- https://pypi.org/project/exotel
