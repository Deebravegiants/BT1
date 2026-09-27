# [H] CVE-2021-33647

## Summary
Severity: High
Advisory: CVE-2021-33647
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-06-27
Source: https://osv.dev/vulnerability/CVE-2021-33647
Type: osv

## Details
When performing the inference shape operation of the Tile operator, if the input data type is not int or int32, it will access data outside of bounds of heap allocated buffers.

## References
- https://gitee.com/mindspore/community/blob/master/security/security_advisory_list/mssa-2021-008_en.md
