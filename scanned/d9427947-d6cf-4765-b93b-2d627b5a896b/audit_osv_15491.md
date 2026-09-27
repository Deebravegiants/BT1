# [C] CVE-2019-16778

## Summary
Severity: Critical
Advisory: CVE-2019-16778
Aliases: GHSA-844w-j86r-4x2j, PYSEC-2019-209, PYSEC-2019-227, PYSEC-2019-234
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-16
Source: https://osv.dev/vulnerability/CVE-2019-16778
Type: osv

## Details
In TensorFlow before 1.15, a heap buffer overflow in UnsortedSegmentSum can be produced when the Index template argument is int32. In this case data_size and num_segments fields are truncated from int64 to int32 and can produce negative numbers, resulting in accessing out of bounds heap memory. This is unlikely to be exploitable and was detected and fixed internally in TensorFlow 1.15 and 2.0.

## References
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/security/advisory/tfsa-2019-002.md
- https://github.com/tensorflow/tensorflow/commit/db4f9717c41bccc3ce10099ab61996b246099892
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-844w-j86r-4x2j
