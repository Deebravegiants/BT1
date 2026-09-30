# [H] CVE-2020-15195

## Summary
Severity: High
Advisory: CVE-2020-15195
Aliases: BIT-tensorflow-2020-15195, GHSA-63xm-rx5p-xvqr, PYSEC-2020-118, PYSEC-2020-275, PYSEC-2020-310
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-25
Source: https://osv.dev/vulnerability/CVE-2020-15195
Type: osv

## Details
In Tensorflow before versions 1.15.4, 2.0.3, 2.1.2, 2.2.1 and 2.3.1, the implementation of `SparseFillEmptyRowsGrad` uses a double indexing pattern. It is possible for `reverse_index_map(i)` to be an index outside of bounds of `grad_values`, thus resulting in a heap buffer overflow. The issue is patched in commit 390611e0d45c5793c7066110af37c8514e6a6c54, and is released in TensorFlow versions 1.15.4, 2.0.3, 2.1.2, 2.2.1, or 2.3.1.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00065.html
- https://github.com/tensorflow/tensorflow/releases/tag/v2.3.1
- https://github.com/tensorflow/tensorflow/commit/390611e0d45c5793c7066110af37c8514e6a6c54
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-63xm-rx5p-xvqr
