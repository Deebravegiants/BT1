# [C] Cobbler vulnerable to arbitrary code execution

## Summary
Severity: Critical
Advisory: GHSA-96hw-v598-jvgh
CVE: CVE-2017-1000469
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-96hw-v598-jvgh
Type: github-advisory

## Affected
- PyPI: `cobbler` — affected >=0 <3.0.0

## Details
Cobbler version up to 2.8.2 is vulnerable to a command injection vulnerability in the "add repo" component resulting in arbitrary code execution as root user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000469
- https://github.com/cobbler/cobbler/issues/1845
- https://github.com/cobbler/cobbler/commit/4b20397425a5d42a2d8927233654f4d7435bd4c2
- https://github.com/cobbler/cobbler
