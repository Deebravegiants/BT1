# [H] CVE-2019-10088

## Summary
Severity: High
Advisory: CVE-2019-10088
Aliases: GHSA-mfwh-gqx8-c787
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-02
Source: https://osv.dev/vulnerability/CVE-2019-10088
Type: osv

## Details
A carefully crafted or corrupt zip file can cause an OOM in Apache Tika's RecursiveParserWrapper in versions 1.7-1.21. Users should upgrade to 1.22 or later.

## References
- https://lists.apache.org/thread.html/1c63555609b737c20d1bbfa4a3e73ec488e3408a84e2f5e47e1b7e08%40%3Cdev.tika.apache.org%3E
- https://lists.apache.org/thread.html/39723d8227b248781898c200aa24b154683673287b150a204b83787d%40%3Cdev.tika.apache.org%3E
- https://lists.apache.org/thread.html/da9ee189d1756f8508d0f2386d8e25aca5a6df541739829232be8a94%40%3Cdev.tika.apache.org%3E
- https://lists.apache.org/thread.html/fb6c84fd387de997e5e366d50b0ca331a328c466432c80f8c5eed33d%40%3Cdev.tika.apache.org%3E
- https://lists.apache.org/thread.html/r204ba2a9ea750f38d789d2bb429cc0925ad6133deea7cbc3001d96b5%40%3Csolr-user.lucene.apache.org%3E
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://security.netapp.com/advisory/ntap-20190828-0004/
