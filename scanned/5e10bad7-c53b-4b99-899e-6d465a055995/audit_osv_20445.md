# [H] CVE-2021-33654

## Summary
Severity: High
Advisory: CVE-2021-33654
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-06-27
Source: https://osv.dev/vulnerability/CVE-2021-33654
Type: osv

## Details
When performing the initialization operation of the Split operator, if a dimension in the input shape is 0, it will cause a division by 0 exception.

## References
- https://gitee.com/mindspore/community/blob/master/security/security_advisory_list/mssa-2021-001_en.md
