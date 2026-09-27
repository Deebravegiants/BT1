# [H] CVE-2021-29608

## Summary
Severity: High
Advisory: CVE-2021-29608
Aliases: BIT-tensorflow-2021-29608, GHSA-rgvq-pcvf-hx75, PYSEC-2021-245, PYSEC-2021-536, PYSEC-2021-734
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-14
Source: https://osv.dev/vulnerability/CVE-2021-29608
Type: osv

## Details
TensorFlow is an end-to-end open source platform for machine learning. Due to lack of validation in `tf.raw_ops.RaggedTensorToTensor`, an attacker can exploit an undefined behavior if input arguments are empty. The implementation(https://github.com/tensorflow/tensorflow/blob/656e7673b14acd7835dc778867f84916c6d1cac2/tensorflow/core/kernels/ragged_tensor_to_tensor_op.cc#L356-L360) only checks that one of the tensors is not empty, but does not check for the other ones. There are multiple `DCHECK` validations to prevent heap OOB, but these are no-op in release builds, hence they don't prevent anything. The fix will be included in TensorFlow 2.5.0. We will also cherrypick these commits on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/b761c9b652af2107cfbc33efd19be0ce41daa33e
- https://github.com/tensorflow/tensorflow/commit/c4d7afb6a5986b04505aca4466ae1951686c80f6
- https://github.com/tensorflow/tensorflow/commit/f94ef358bb3e91d517446454edff6535bcfe8e4a
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-rgvq-pcvf-hx75
