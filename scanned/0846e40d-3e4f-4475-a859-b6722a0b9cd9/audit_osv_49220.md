# [M] CVE-2018-6554

## Summary
Severity: Medium
Advisory: CVE-2018-6554
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-09-04
Source: https://osv.dev/vulnerability/CVE-2018-6554
Type: osv

## Details
Memory leak in the irda_bind function in net/irda/af_irda.c and later in drivers/staging/irda/net/af_irda.c in the Linux kernel before 4.17 allows local users to cause a denial of service (memory consumption) by repeatedly binding an AF_IRDA socket.

## References
- https://lists.debian.org/debian-lts-announce/2019/03/msg00017.html
- https://usn.ubuntu.com/3775-2/
- https://usn.ubuntu.com/3776-2/
- https://usn.ubuntu.com/3777-1/
- https://usn.ubuntu.com/3777-3/
- https://www.debian.org/security/2018/dsa-4308
- https://lists.debian.org/debian-lts-announce/2018/10/msg00003.html
- https://usn.ubuntu.com/3775-1/
- https://usn.ubuntu.com/3776-1/
- https://usn.ubuntu.com/3777-2/
- http://www.securityfocus.com/bid/105302
- https://www.spinics.net/lists/stable/msg255034.html
- https://www.spinics.net/lists/stable/msg255030.html
