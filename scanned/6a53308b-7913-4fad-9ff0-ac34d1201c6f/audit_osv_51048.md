# [H] CVE-2021-0707

## Summary
Severity: High
Advisory: CVE-2021-0707
Aliases: A-155756045, ASB-A-155756045
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-12
Source: https://osv.dev/vulnerability/CVE-2021-0707
Type: osv

## Details
In dma_buf_release of dma-buf.c, there is a possible memory corruption due to a use after free. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-155756045References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2022-04-01
- https://source.android.com/security/bulletin/2022-04-01
