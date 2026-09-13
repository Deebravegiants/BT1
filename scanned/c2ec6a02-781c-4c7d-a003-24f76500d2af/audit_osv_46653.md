# [H] CVE-2014-6262

## Summary
Severity: High
Advisory: CVE-2014-6262
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-02-12
Source: https://osv.dev/vulnerability/CVE-2014-6262
Type: osv

## Details
Multiple format string vulnerabilities in the python module in RRDtool, as used in Zenoss Core before 4.2.5 and other products, allow remote attackers to execute arbitrary code or cause a denial of service (application crash) via a crafted third argument to the rrdtool.graph function, aka ZEN-15415, a related issue to CVE-2013-2131.

## References
- http://www.kb.cert.org/vuls/id/449452
- https://docs.google.com/spreadsheets/d/1dHAc4PxUbs-4Dxzm1wSCE0sMz5UCMY6SW3PlMHSyuuQ/edit?usp=sharing
- https://github.com/oetiker/rrdtool-1.x/commit/64ed5314af1255ab6dded45f70b39cdeab5ae2ec
- https://github.com/oetiker/rrdtool-1.x/commit/85261a013112e278c90224033f5b0592ee387786
- https://github.com/oetiker/rrdtool-1.x/pull/532
- https://lists.debian.org/debian-lts-announce/2020/03/msg00000.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00003.html
- https://www.securityfocus.com/bid/71540
- https://lists.debian.org/debian-lts-announce/2020/03/msg00000.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00003.html
- https://github.com/oetiker/rrdtool-1.x/commit/64ed5314af1255ab6dded45f70b39cdeab5ae2ec
- https://github.com/oetiker/rrdtool-1.x/commit/85261a013112e278c90224033f5b0592ee387786
- http://www.kb.cert.org/vuls/id/449452
