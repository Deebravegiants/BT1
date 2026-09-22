# [M] CVE-2017-13729

## Summary
Severity: Medium
Advisory: CVE-2017-13729
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-29
Source: https://osv.dev/vulnerability/CVE-2017-13729
Type: osv

## Details
There is an illegal address access in the _nc_save_str function in alloc_entry.c in ncurses 6.0. It will lead to a remote denial of service attack.

## References
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://security.gentoo.org/glsa/201804-13
- https://bugzilla.redhat.com/show_bug.cgi?id=1484276
