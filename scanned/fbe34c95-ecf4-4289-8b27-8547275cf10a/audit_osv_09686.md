# [C] CVE-2017-10684

## Summary
Severity: Critical
Advisory: CVE-2017-10684
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-29
Source: https://osv.dev/vulnerability/CVE-2017-10684
Type: osv

## Details
In ncurses 6.0, there is a stack-based buffer overflow in the fmt_entry function. A crafted input will lead to a remote arbitrary code execution attack.

## References
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://security.gentoo.org/glsa/201804-13
- https://bugzilla.redhat.com/show_bug.cgi?id=1464687
