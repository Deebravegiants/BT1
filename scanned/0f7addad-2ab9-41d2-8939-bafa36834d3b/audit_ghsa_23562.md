# [M] FTP backend for Duplicity Discloses Passwords to Process Listing

## Summary
Severity: Medium
Advisory: GHSA-wxcw-rqxc-hj85
CVE: CVE-2007-5201
CWE: CWE-200
Ecosystem: PyPI
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-wxcw-rqxc-hj85
Type: github-advisory

## Affected
- PyPI: `duplicity` — affected >=0 <0.4.9

## Details
The FTP backend for Duplicity before 0.4.9 sends the password as a command line argument when calling ncftp, which might allow local users to read the password by listing the process and its arguments.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-5201
- https://bugzilla.redhat.com/show_bug.cgi?id=293081
- https://gitlab.com/duplicity/duplicity
- https://web.archive.org/web/20080118045107/https://duplicity.nongnu.org/CHANGELOG
- https://web.archive.org/web/20200228164800/http://www.securityfocus.com/bid/27771
- https://www.redhat.com/archives/fedora-package-announce/2008-February/msg00356.html
- https://www.redhat.com/archives/fedora-package-announce/2008-February/msg00445.html
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=442840
