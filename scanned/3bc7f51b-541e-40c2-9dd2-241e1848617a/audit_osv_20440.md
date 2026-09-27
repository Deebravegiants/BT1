# [H] CVE-2021-33649

## Summary
Severity: High
Advisory: CVE-2021-33649
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-06-27
Source: https://osv.dev/vulnerability/CVE-2021-33649
Type: osv

## Details
When performing the inference shape operation of the Transpose operator, if the value in the perm element is greater than or equal to the size of the input_shape, it will access data outside of bounds of input_shape which allocated from heap buffers.

## References
- https://gitee.com/mindspore/community/blob/master/security/security_advisory_list/mssa-2021-006_en.md
