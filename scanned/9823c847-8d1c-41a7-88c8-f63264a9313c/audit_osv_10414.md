# [M] CVE-2017-15298

## Summary
Severity: Medium
Advisory: CVE-2017-15298
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-14
Source: https://osv.dev/vulnerability/CVE-2017-15298
Type: osv

## Details
Git through 2.14.2 mishandles layers of tree objects, which allows remote attackers to cause a denial of service (memory consumption) via a crafted repository, aka a Git bomb. This can also have an impact of disk consumption; however, an affected process typically would not survive its attempt to build the data structure in memory before writing to disk.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00003.html
- https://usn.ubuntu.com/3829-1/
- https://github.com/Katee/git-bomb
- https://kate.io/blog/git-bomb/
