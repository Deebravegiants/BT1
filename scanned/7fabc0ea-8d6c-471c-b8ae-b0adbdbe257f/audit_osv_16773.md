# [H] CVE-2019-9674

## Summary
Severity: High
Advisory: CVE-2019-9674
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-02-04
Source: https://osv.dev/vulnerability/CVE-2019-9674
Type: osv

## Details
Lib/zipfile.py in Python through 3.7.2 allows remote attackers to cause a denial of service (resource consumption) via a ZIP bomb.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00041.html
- https://github.com/python/cpython/blob/master/Lib/zipfile.py
- https://python-security.readthedocs.io/security.html#archives-and-zip-bomb
- https://security.netapp.com/advisory/ntap-20200221-0003/
- https://usn.ubuntu.com/4428-1/
- https://www.python.org/news/security/
- https://bugs.python.org/issue36260
- https://bugs.python.org/issue36462
