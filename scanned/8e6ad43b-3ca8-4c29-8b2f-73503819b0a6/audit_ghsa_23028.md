# [C] Dulwich Buffer Overflow when handling pack files

## Summary
Severity: Critical
Advisory: GHSA-vjjf-3rvg-gv3v
CVE: CVE-2015-0838
CWE: CWE-119
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-vjjf-3rvg-gv3v
Type: github-advisory

## Affected
- PyPI: `dulwich` — affected >=0 <0.9.9

## Details
Buffer overflow in the C implementation of the `apply_delta` function `in _pack.c` in Dulwich before 0.9.9 allows remote attackers to execute arbitrary code via a crafted pack file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-0838
- https://github.com/jelmer/dulwich
- https://github.com/pypa/advisory-database/tree/main/vulns/dulwich/PYSEC-2015-35.yaml
- https://lists.launchpad.net/dulwich-users/msg00829.html
- http://www.debian.org/security/2015/dsa-3206
