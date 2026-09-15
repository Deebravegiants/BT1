# [H] CVE-2021-33653

## Summary
Severity: High
Advisory: CVE-2021-33653
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-06-27
Source: https://osv.dev/vulnerability/CVE-2021-33653
Type: osv

## Details
When performing the derivation shape operation of the SpaceToBatch operator, if there is a value of 0 in the parameter block_shape element, it will cause a division by 0 exception.

## References
- https://gitee.com/mindspore/community/blob/master/security/security_advisory_list/mssa-2021-002_en.md
