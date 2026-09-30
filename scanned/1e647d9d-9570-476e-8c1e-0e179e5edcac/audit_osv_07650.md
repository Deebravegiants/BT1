# [M] Segfault in `CTCBeamSearchDecoder`

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2021-29581
Aliases: CVE-2021-29581, GHSA-vq2r-5xvm-3hc3, PYSEC-2021-218, PYSEC-2021-509, PYSEC-2021-707
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29581
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. Due to lack of validation in `tf.raw_ops.CTCBeamSearchDecoder`, an attacker can trigger denial of service via segmentation faults. The implementation(https://github.com/tensorflow/tensorflow/blob/a74768f8e4efbda4def9f16ee7e13cf3922ac5f7/tensorflow/core/kernels/ctc_decoder_ops.cc#L68-L79) fails to detect cases when the input tensor is empty and proceeds to read data from a null buffer. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/b1b323042264740c398140da32e93fb9c2c9f33e
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-vq2r-5xvm-3hc3
- https://nvd.nist.gov/vuln/detail/CVE-2021-29581
