# [M] CVE-2021-39648

## Summary
Severity: Medium
Advisory: CVE-2021-39648
Aliases: A-160822094, PUB-A-160822094
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-12-15
Source: https://osv.dev/vulnerability/CVE-2021-39648
Type: osv

## Details
In gadget_dev_desc_UDC_show of configfs.c, there is a possible disclosure of kernel heap memory due to a race condition. This could lead to local information disclosure with System execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-160822094References: Upstream kernel

## References
- https://source.android.com/security/bulletin/pixel/2021-12-01
- https://source.android.com/security/bulletin/pixel/2021-12-01
