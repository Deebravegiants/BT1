# [H] CVE-2020-1752

## Summary
Severity: High
Advisory: CVE-2020-1752
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-04-30
Source: https://osv.dev/vulnerability/CVE-2020-1752
Type: osv

## Details
A use-after-free vulnerability introduced in glibc upstream version 2.14 was found in the way the tilde expansion was carried out. Directory paths containing an initial tilde followed by a valid username were affected by this issue. A local attacker could exploit this flaw by creating a specially crafted path that, when processed by the glob function, would potentially lead to arbitrary code execution. This was fixed in version 2.32.

## References
- https://sourceware.org/git/gitweb.cgi?p=glibc.git%3Bh=ddc650e9b3dc916eab417ce9f79e67337b05035c
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://usn.ubuntu.com/4416-1/
- https://security.gentoo.org/glsa/202101-20
- https://lists.debian.org/debian-lts-announce/2022/10/msg00021.html
- https://security.netapp.com/advisory/ntap-20200511-0005/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1752
- https://sourceware.org/bugzilla/show_bug.cgi?id=25414
