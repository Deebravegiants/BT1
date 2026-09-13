# [H] CVE-2018-6555

## Summary
Severity: High
Advisory: CVE-2018-6555
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-04
Source: https://osv.dev/vulnerability/CVE-2018-6555
Type: osv

## Details
The irda_setsockopt function in net/irda/af_irda.c and later in drivers/staging/irda/net/af_irda.c in the Linux kernel before 4.17 allows local users to cause a denial of service (ias_object use-after-free and system crash) or possibly have unspecified other impact via an AF_IRDA socket.

## References
- http://www.securityfocus.com/bid/105304
- https://lists.debian.org/debian-lts-announce/2018/10/msg00003.html
- https://usn.ubuntu.com/3775-1/
- https://usn.ubuntu.com/3775-2/
- https://usn.ubuntu.com/3776-2/
- https://usn.ubuntu.com/3777-2/
- https://usn.ubuntu.com/3776-1/
- https://usn.ubuntu.com/3777-1/
- https://usn.ubuntu.com/3777-3/
- https://www.debian.org/security/2018/dsa-4308
- https://www.spinics.net/lists/stable/msg255031.html
- https://www.spinics.net/lists/stable/msg255035.html
