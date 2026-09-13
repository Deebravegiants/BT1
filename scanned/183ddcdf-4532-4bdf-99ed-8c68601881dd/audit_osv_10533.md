# [H] CVE-2017-16879

## Summary
Severity: High
Advisory: CVE-2017-16879
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-11-22
Source: https://osv.dev/vulnerability/CVE-2017-16879
Type: osv

## Details
Stack-based buffer overflow in the _nc_write_entry function in tinfo/write_entry.c in ncurses 6.0 allows attackers to cause a denial of service (application crash) or possibly execute arbitrary code via a crafted terminfo file, as demonstrated by tic.

## References
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- http://invisible-island.net/ncurses/NEWS.html#t20171125
- http://packetstormsecurity.com/files/145045/GNU-ncurses-6.0-tic-Denial-Of-Service.html
- https://security.gentoo.org/glsa/201804-13
- https://tools.cisco.com/security/center/viewAlert.x?alertId=57695
