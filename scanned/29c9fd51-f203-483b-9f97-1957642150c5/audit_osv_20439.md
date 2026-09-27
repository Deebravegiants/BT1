# [H] CVE-2021-33648

## Summary
Severity: High
Advisory: CVE-2021-33648
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-06-27
Source: https://osv.dev/vulnerability/CVE-2021-33648
Type: osv

## Details
When performing the inference shape operation of Affine, Concat, MatMul, ArgMinMax, EmbeddingLookup, and Gather operators, if the input shape size is 0, it will access data outside of bounds of shape which allocated from heap buffers.

## References
- https://gitee.com/mindspore/community/blob/master/security/security_advisory_list/mssa-2021-007_en.md
