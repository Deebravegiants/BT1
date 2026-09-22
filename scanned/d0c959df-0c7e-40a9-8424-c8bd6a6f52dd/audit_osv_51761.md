# [M] CVE-2021-39657

## Summary
Severity: Medium
Advisory: CVE-2021-39657
Aliases: A-194696049, PUB-A-194696049
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-12-15
Source: https://osv.dev/vulnerability/CVE-2021-39657
Type: osv

## Details
In ufshcd_eh_device_reset_handler of ufshcd.c, there is a possible out of bounds read due to a missing bounds check. This could lead to local information disclosure with System execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-194696049References: Upstream kernel

## References
- https://source.android.com/security/bulletin/pixel/2021-12-01
- https://source.android.com/security/bulletin/pixel/2021-12-01
