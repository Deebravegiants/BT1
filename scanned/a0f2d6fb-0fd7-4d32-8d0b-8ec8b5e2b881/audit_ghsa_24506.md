# [C] web2py is vulnerable to password brute-force attack

## Summary
Severity: Critical
Advisory: GHSA-gv85-wgxc-vc56
CVE: CVE-2016-10321
CWE: CWE-307
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-gv85-wgxc-vc56
Type: github-advisory

## Affected
- PyPI: `web2py` — affected >=0 <2.14.6

## Details
web2py before 2.14.6 does not properly check if a host is denied before verifying passwords, allowing a remote attacker to perform brute-force attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10321
- https://github.com/web2py/web2py/issues/1585#issuecomment-284317919
- https://github.com/web2py/web2py/commit/944d8bd8f3c5cf8ae296fc03d149056c65358426
- https://github.com/web2py/web2py
- https://usn.ubuntu.com/4030-1
