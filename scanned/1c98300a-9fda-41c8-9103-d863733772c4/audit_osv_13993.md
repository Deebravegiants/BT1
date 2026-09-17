# [M] CVE-2018-6198

## Summary
Severity: Medium
Advisory: CVE-2018-6198
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-01-25
Source: https://osv.dev/vulnerability/CVE-2018-6198
Type: osv

## Details
w3m through 0.5.3 does not properly handle temporary files when the ~/.w3m directory is unwritable, which allows a local attacker to craft a symlink attack to overwrite arbitrary files.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00028.html
- http://www.securityfocus.com/bid/102855
- https://usn.ubuntu.com/3555-1/
- https://usn.ubuntu.com/3555-2/
- https://bugs.debian.org/888097
- https://github.com/tats/w3m/commit/18dcbadf2771cdb0c18509b14e4e73505b242753
- https://salsa.debian.org/debian/w3m/commit/18dcbadf2771cdb0c18509b14e4e73505b242753
