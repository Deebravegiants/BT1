# [M] CVE-2018-1324

## Summary
Severity: Medium
Advisory: CVE-2018-1324
Aliases: GHSA-h436-432x-8fvx
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-16
Source: https://osv.dev/vulnerability/CVE-2018-1324
Type: osv

## Details
A specially crafted ZIP archive can be used to cause an infinite loop inside of Apache Commons Compress' extra field parser used by the ZipFile and ZipArchiveInputStream classes in versions 1.11 to 1.15. This can be used to mount a denial of service attack against services that use Compress' zip package.

## References
- https://lists.apache.org/thread.html/1c7b6df6d1c5c8583518a0afa017782924918e4d6acfaf23ed5b2089%40%3Cdev.commons.apache.org%3E
- https://lists.apache.org/thread.html/b8ef29df0f1d55aa741170748352ae8e425c7b1d286b2f257711a2dd%40%3Cdev.creadur.apache.org%3E
- https://lists.apache.org/thread.html/ff8dcfe29377088ab655fda9d585dccd5b1f07fabd94ae84fd60a7f8%40%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/r5532dc8d5456b5151e8c286801e2e5769f5c04118b29c3b5d13ea387%40%3Cissues.beam.apache.org%3E
- http://www.securityfocus.com/bid/103490
- http://www.securitytracker.com/id/1040549
- https://www.oracle.com/security-alerts/cpujan2022.html
