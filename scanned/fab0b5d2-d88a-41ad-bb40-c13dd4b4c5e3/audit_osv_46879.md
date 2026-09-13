# [M] CVE-2015-7555

## Summary
Severity: Medium
Advisory: CVE-2015-7555
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-04-13
Source: https://osv.dev/vulnerability/CVE-2015-7555
Type: osv

## Details
Heap-based buffer overflow in giffix.c in giffix in giflib 5.1.1 allows attackers to cause a denial of service (program crash) via crafted image and logical screen width fields in a GIF file.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/174876.html
- http://packetstormsecurity.com/files/135034/giflib-5.1.1-Heap-Overflow.html
- http://seclists.org/fulldisclosure/2015/Dec/83
- http://www-01.ibm.com/support/docview.wss?uid=isg3T1023474
- http://www.securityfocus.com/archive/1/537171/100/0/threaded
- http://www.securityfocus.com/bid/81697
- http://www.securitytracker.com/id/1035331
- https://source.android.com/security/bulletin/2017-05-01
