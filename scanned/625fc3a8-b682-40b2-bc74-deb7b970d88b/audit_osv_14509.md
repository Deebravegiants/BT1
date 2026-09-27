# [M] CVE-2019-10093

## Summary
Severity: Medium
Advisory: CVE-2019-10093
Aliases: GHSA-4mq5-mj59-qq9c
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-08-02
Source: https://osv.dev/vulnerability/CVE-2019-10093
Type: osv

## Details
In Apache Tika 1.19 to 1.21, a carefully crafted 2003ml or 2006ml file could consume all available SAXParsers in the pool and lead to very long hangs. Apache Tika users should upgrade to 1.22 or later.

## References
- https://lists.apache.org/thread.html/39723d8227b248781898c200aa24b154683673287b150a204b83787d%40%3Cdev.tika.apache.org%3E
- https://lists.apache.org/thread.html/a5a44eff1b9eda3bc69d22943a1030c43d376380c75d3ab04d0c1a21%40%3Cdev.tika.apache.org%3E
- https://lists.apache.org/thread.html/da9ee189d1756f8508d0f2386d8e25aca5a6df541739829232be8a94%40%3Cdev.tika.apache.org%3E
- https://lists.apache.org/thread.html/fb6c84fd387de997e5e366d50b0ca331a328c466432c80f8c5eed33d%40%3Cdev.tika.apache.org%3E
- https://lists.apache.org/thread.html/r204ba2a9ea750f38d789d2bb429cc0925ad6133deea7cbc3001d96b5%40%3Csolr-user.lucene.apache.org%3E
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://security.netapp.com/advisory/ntap-20190828-0004/
