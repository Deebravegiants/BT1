# [M] CVE-2020-15198

## Summary
Severity: Medium
Advisory: CVE-2020-15198
Aliases: BIT-tensorflow-2020-15198, GHSA-jc87-6vpp-7ff3, PYSEC-2020-121, PYSEC-2020-278, PYSEC-2020-313
CVSS: 5.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2020-09-25
Source: https://osv.dev/vulnerability/CVE-2020-15198
Type: osv

## Details
In Tensorflow before version 2.3.1, the `SparseCountSparseOutput` implementation does not validate that the input arguments form a valid sparse tensor. In particular, there is no validation that the `indices` tensor has the same shape as the `values` one. The values in these tensors are always accessed in parallel. Thus, a shape mismatch can result in accesses outside the bounds of heap allocated buffers. The issue is patched in commit 3cbb917b4714766030b28eba9fb41bb97ce9ee02 and is released in TensorFlow version 2.3.1.

## References
- https://github.com/tensorflow/tensorflow/releases/tag/v2.3.1
- https://github.com/tensorflow/tensorflow/commit/3cbb917b4714766030b28eba9fb41bb97ce9ee02
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-jc87-6vpp-7ff3
