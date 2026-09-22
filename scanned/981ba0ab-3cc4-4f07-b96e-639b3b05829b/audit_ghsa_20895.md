# [C] python-scciclient vulnerable to Man-in-the-middle (MITM) attacks

## Summary
Severity: Critical
Advisory: GHSA-rf3f-3p37-2qh4
CVE: CVE-2022-2996
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-09-02
Source: https://github.com/advisories/GHSA-rf3f-3p37-2qh4
Type: github-advisory

## Affected
- PyPI: `python-scciclient` — affected >=0 <0.12.0

## Details
A flaw was found in the python-scciclient when making an HTTPS connection to a server where the server's certificate would not be verified. This issue opens up the connection to possible Man-in-the-middle (MITM) attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2996
- https://github.com/openstack-archive/python-scciclient
- https://github.com/pypa/advisory-database/tree/main/vulns/python-scciclient/PYSEC-2022-43152.yaml
- https://lists.debian.org/debian-lts-announce/2022/11/msg00006.html
- https://opendev.org/x/python-scciclient/commit/274dca0344b65b4ac113d3271d21c17e970a636c
