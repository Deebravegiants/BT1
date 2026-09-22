# [H] CVE-2017-12613

## Summary
Severity: High
Advisory: CVE-2017-12613
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-10-24
Source: https://osv.dev/vulnerability/CVE-2017-12613
Type: osv

## Details
When apr_time_exp*() or apr_os_exp_time*() functions are invoked with an invalid month field value in Apache Portable Runtime APR 1.6.2 and prior, out of bounds memory may be accessed in converting this value to an apr_time_exp_t value, potentially revealing the contents of a different static heap value or resulting in program termination, and may represent an information disclosure or denial of service vulnerability to applications which call these APR functions with unvalidated external input.

## References
- http://www.securityfocus.com/bid/101560
- https://lists.apache.org/thread.html/r270dd5022db194b78acaf509216a33c85f3da43757defa05cc766339%40%3Ccommits.apr.apache.org%3E
- https://lists.apache.org/thread.html/ra2868b53339a6af65577146ad87016368c138388b09bff9d2860f50e%40%3Cdev.apr.apache.org%3E
- https://lists.apache.org/thread.html/ra38094406cc38a05218ebd1158187feda021b0c3a1df400bbf296af8%40%3Cdev.apr.apache.org%3E
- https://lists.apache.org/thread.html/rb1f3c85f50fbd924a0051675118d1609e57957a02ece7facb723155b%40%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/rcc48a0acebbd74bbdeebc02ff228bb72c0631b21823fffe27d4691e9%40%3Ccommits.apr.apache.org%3E
- http://www.apache.org/dist/apr/Announcement1.x.html
- http://www.openwall.com/lists/oss-security/2021/08/23/1
- http://www.securitytracker.com/id/1042004
- https://access.redhat.com/errata/RHSA-2017:3270
- https://access.redhat.com/errata/RHSA-2017:3475
- https://access.redhat.com/errata/RHSA-2017:3476
- https://access.redhat.com/errata/RHSA-2017:3477
- https://access.redhat.com/errata/RHSA-2018:0316
- https://access.redhat.com/errata/RHSA-2018:0465
- https://access.redhat.com/errata/RHSA-2018:0466
- https://access.redhat.com/errata/RHSA-2018:1253
- https://lists.debian.org/debian-lts-announce/2017/11/msg00005.html
- https://lists.debian.org/debian-lts-announce/2022/01/msg00023.html
- https://lists.apache.org/thread.html/12489f2e4a9f9d390235c16298aca0d20658789de80d553513977f13%40%3Cannounce.apache.org%3E
