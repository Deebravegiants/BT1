# [M] CVE-2021-28657

## Summary
Severity: Medium
Advisory: CVE-2021-28657
Aliases: GHSA-567x-m4wm-87v8
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-03-31
Source: https://osv.dev/vulnerability/CVE-2021-28657
Type: osv

## Details
A carefully crafted or corrupt file may trigger an infinite loop in Tika's MP3Parser up to and including Tika 1.25. Apache Tika users should upgrade to 1.26 or later.

## References
- https://lists.apache.org/thread.html/r4cbc3f6981cd0a1a482531df9d44e4c42a7f63342a7ba78b7bff8a1b%40%3Cnotifications.james.apache.org%3E
- https://lists.apache.org/thread.html/r915add4aa52c60d1b5cf085039cfa73a98d7fae9673374dfd7744b5a%40%3Cdev.tika.apache.org%3E
- https://security.netapp.com/advisory/ntap-20210507-0004/
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
