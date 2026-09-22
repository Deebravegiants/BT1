# [H] CVE-2018-6954

## Summary
Severity: High
Advisory: CVE-2018-6954
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-13
Source: https://osv.dev/vulnerability/CVE-2018-6954
Type: osv

## Details
systemd-tmpfiles in systemd through 237 mishandles symlinks present in non-terminal path components, which allows local users to obtain ownership of arbitrary files via vectors involving creation of a directory and a file under that directory, and later replacing that directory with a symlink. This occurs even if the fs.protected_symlinks sysctl is turned on.

## References
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00062.html
- https://usn.ubuntu.com/3816-1/
- https://usn.ubuntu.com/3816-2/
- https://github.com/systemd/systemd/issues/7986
