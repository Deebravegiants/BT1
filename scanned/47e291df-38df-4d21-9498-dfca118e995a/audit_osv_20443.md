# [H] CVE-2021-33652

## Summary
Severity: High
Advisory: CVE-2021-33652
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-06-27
Source: https://osv.dev/vulnerability/CVE-2021-33652
Type: osv

## Details
When the Reduce operator run operation is executed, if there is a value of 0 in the parameter axis_sizes element, it will cause a division by 0 exception.

## References
- https://gitee.com/mindspore/community/blob/master/security/security_advisory_list/mssa-2021-003_en.md
