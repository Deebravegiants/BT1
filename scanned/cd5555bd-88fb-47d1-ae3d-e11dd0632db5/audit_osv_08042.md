# [H] CVE-2016-10087

## Summary
Severity: High
Advisory: CVE-2016-10087
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-30
Source: https://osv.dev/vulnerability/CVE-2016-10087
Type: osv

## Details
The png_set_text_2 function in libpng 0.71 before 1.0.67, 1.2.x before 1.2.57, 1.4.x before 1.4.20, 1.5.x before 1.5.28, and 1.6.x before 1.6.27 allows context-dependent attackers to cause a NULL pointer dereference vectors involving loading a text chunk into a png structure, removing the text, and then adding another text chunk to the structure.

## References
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://usn.ubuntu.com/3712-1/
- https://usn.ubuntu.com/3712-2/
- http://www.openwall.com/lists/oss-security/2016/12/29/2
- http://www.openwall.com/lists/oss-security/2016/12/30/4
- http://www.securityfocus.com/bid/95157
- https://security.gentoo.org/glsa/201701-74
