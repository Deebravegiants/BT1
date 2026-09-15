# [M] CVE-2021-37688

## Summary
Severity: Medium
Advisory: CVE-2021-37688
Aliases: BIT-tensorflow-2021-37688, GHSA-vcjj-9vg7-vf68, PYSEC-2021-310, PYSEC-2021-601, PYSEC-2021-799
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-12
Source: https://osv.dev/vulnerability/CVE-2021-37688
Type: osv

## Details
TensorFlow is an end-to-end open source platform for machine learning. In affected versions an attacker can craft a TFLite model that would trigger a null pointer dereference, which would result in a crash and denial of service. The [implementation](https://github.com/tensorflow/tensorflow/blob/149562d49faa709ea80df1d99fc41d005b81082a/tensorflow/lite/kernels/internal/optimized/optimized_ops.h#L268-L285) unconditionally dereferences a pointer. We have patched the issue in GitHub commit 15691e456c7dc9bd6be203b09765b063bf4a380c. The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-vcjj-9vg7-vf68
- https://github.com/tensorflow/tensorflow/commit/15691e456c7dc9bd6be203b09765b063bf4a380c
