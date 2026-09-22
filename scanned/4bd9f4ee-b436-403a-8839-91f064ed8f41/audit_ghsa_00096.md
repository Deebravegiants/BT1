# [H] Pyro mishandles pid files in temporary directory locations and opening the pid file as root

## Summary
Severity: High
Advisory: GHSA-xrr4-74mc-rpjc
CVE: CVE-2011-2765
CWE: CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-08-21
Source: https://github.com/advisories/GHSA-xrr4-74mc-rpjc
Type: github-advisory

## Affected
- PyPI: `pyro` — affected >=0 <3.15

## Details
pyro before 3.15 unsafely handles pid files in temporary directory locations and opening the pid file as root. An attacker can use this flaw to overwrite arbitrary files via symlinks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-2765
- https://github.com/irmen/Pyro3/commit/554e095a62c4412c91f981e72fd34a936ac2bf1e
- https://bugs.debian.org/631912
- https://github.com/irmen/Pyro3
- https://github.com/pypa/advisory-database/tree/main/vulns/pyro/PYSEC-2018-99.yaml
- https://pythonhosted.org/Pyro/12-changes.html
