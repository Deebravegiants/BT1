# [M] eyeD3 is vulnerable to arbitrary file modification via symlink attack

## Summary
Severity: Medium
Advisory: GHSA-4r2w-w73w-36jm
CVE: CVE-2014-1934
CWE: CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-4r2w-w73w-36jm
Type: github-advisory

## Affected
- PyPI: `eyeD3` — affected >=0 <0.7.5

## Details
tag.py in eyeD3 (aka python-eyed3) 0.7.5 and earlier for Python allows local users to modify arbitrary files via a symlink attack on a temporary file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-1934
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=737062
- https://bugzilla.redhat.com/show_bug.cgi?id=1063671
- https://github.com/nicfit/eyeD3
- https://koji.fedoraproject.org/koji/buildinfo?buildID=594272
- http://lists.opensuse.org/opensuse-updates/2014-05/msg00027.html
- http://lists.opensuse.org/opensuse-updates/2014-05/msg00028.html
