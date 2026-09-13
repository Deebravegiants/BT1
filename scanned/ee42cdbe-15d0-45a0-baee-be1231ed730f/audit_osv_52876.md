# [M] CVE-2022-20008

## Summary
Severity: Medium
Advisory: CVE-2022-20008
Aliases: A-216481035, ASB-A-216481035
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-05-10
Source: https://osv.dev/vulnerability/CVE-2022-20008
Type: osv

## Details
In mmc_blk_read_single of block.c, there is a possible way to read kernel heap memory due to uninitialized data. This could lead to local information disclosure if reading from an SD card that triggers errors, with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-216481035References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2022-05-01
