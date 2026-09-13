# [M] CVE-2020-15201

## Summary
Severity: Medium
Advisory: CVE-2020-15201
Aliases: BIT-tensorflow-2020-15201, GHSA-p5f8-gfw5-33w4, PYSEC-2020-124, PYSEC-2020-281, PYSEC-2020-316
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2020-09-25
Source: https://osv.dev/vulnerability/CVE-2020-15201
Type: osv

## Details
In Tensorflow before version 2.3.1, the `RaggedCountSparseOutput` implementation does not validate that the input arguments form a valid ragged tensor. In particular, there is no validation that the values in the `splits` tensor generate a valid partitioning of the `values` tensor. Hence, the code is prone to heap buffer overflow. If `split_values` does not end with a value at least `num_values` then the `while` loop condition will trigger a read outside of the bounds of `split_values` once `batch_idx` grows too large. The issue is patched in commit 3cbb917b4714766030b28eba9fb41bb97ce9ee02 and is released in TensorFlow version 2.3.1.

## References
- https://github.com/tensorflow/tensorflow/releases/tag/v2.3.1
- https://github.com/tensorflow/tensorflow/commit/3cbb917b4714766030b28eba9fb41bb97ce9ee02
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-p5f8-gfw5-33w4
