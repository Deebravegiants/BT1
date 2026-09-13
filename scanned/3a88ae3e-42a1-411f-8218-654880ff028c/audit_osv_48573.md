# [H] CVE-2017-9725

## Summary
Severity: High
Advisory: CVE-2017-9725
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-21
Source: https://osv.dev/vulnerability/CVE-2017-9725
Type: osv

## Details
In all Qualcomm products with Android releases from CAF using the Linux kernel, during DMA allocation, due to wrong data type of size, allocation size gets truncated which makes allocation succeed when it should fail.

## References
- https://access.redhat.com/errata/RHSA-2018:0676
- https://access.redhat.com/errata/RHSA-2018:1062
- https://access.redhat.com/errata/RHSA-2018:1130
- https://access.redhat.com/errata/RHSA-2018:1170
- http://www.securityfocus.com/bid/100658
- https://source.android.com/security/bulletin/2017-09-01
