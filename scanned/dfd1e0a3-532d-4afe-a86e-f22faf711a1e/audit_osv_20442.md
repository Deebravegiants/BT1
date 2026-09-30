# [H] CVE-2021-33651

## Summary
Severity: High
Advisory: CVE-2021-33651
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-06-27
Source: https://osv.dev/vulnerability/CVE-2021-33651
Type: osv

## Details
When performing the analytical operation of the DepthwiseConv2D operator, if the attribute depth_multiplier is 0, it will cause a division by 0 exception.

## References
- https://gitee.com/mindspore/community/blob/master/security/security_advisory_list/mssa-2021-004_en.md
