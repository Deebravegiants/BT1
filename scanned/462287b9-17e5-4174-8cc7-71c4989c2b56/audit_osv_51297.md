# [H] CVE-2021-27379

## Summary
Severity: High
Advisory: CVE-2021-27379
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-18
Source: https://osv.dev/vulnerability/CVE-2021-27379
Type: osv

## Details
An issue was discovered in Xen through 4.11.x, allowing x86 Intel HVM guest OS users to achieve unintended read/write DMA access, and possibly cause a denial of service (host OS crash) or gain privileges. This occurs because a backport missed a flush, and thus IOMMU updates were not always correct. NOTE: this issue exists because of an incomplete fix for CVE-2020-15565.

## References
- http://www.openwall.com/lists/oss-security/2021/02/23/1
- https://www.debian.org/security/2021/dsa-4888
- http://xenbits.xen.org/xsa/advisory-366.html
- https://xenbits.xen.org/xsa/advisory-366.html
