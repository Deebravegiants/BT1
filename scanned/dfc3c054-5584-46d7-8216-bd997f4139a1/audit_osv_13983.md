# [H] CVE-2018-5968

## Summary
Severity: High
Advisory: CVE-2018-5968
Aliases: GHSA-w3f4-3q6j-rh82
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-22
Source: https://osv.dev/vulnerability/CVE-2018-5968
Type: osv

## Details
FasterXML jackson-databind through 2.8.11 and 2.9.x through 2.9.3 allows unauthenticated remote code execution because of an incomplete fix for the CVE-2017-7525 and CVE-2017-17485 deserialization flaws. This is exploitable via two different gadgets that bypass a blacklist.

## References
- https://access.redhat.com/errata/RHSA-2018:0478
- https://access.redhat.com/errata/RHSA-2018:0479
- https://access.redhat.com/errata/RHSA-2018:0480
- https://access.redhat.com/errata/RHSA-2018:0481
- https://access.redhat.com/errata/RHSA-2018:1525
- https://access.redhat.com/errata/RHSA-2019:2858
- https://access.redhat.com/errata/RHSA-2019:3149
- https://github.com/FasterXML/jackson-databind/issues/1899
- https://security.netapp.com/advisory/ntap-20180423-0002/
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03902en_us
- https://www.debian.org/security/2018/dsa-4114
- https://www.oracle.com/security-alerts/cpuoct2020.html
