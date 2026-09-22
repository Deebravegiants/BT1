# [H] Lack of validation in data format attributes in TensorFlow

## Summary
Severity: High
Advisory: BIT-tensorflow-2020-26267
Aliases: CVE-2020-26267, GHSA-c9f3-9wfr-wgh7, PYSEC-2020-140, PYSEC-2020-298, PYSEC-2020-333
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2020-26267
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.3.0 <2.3.2

## Details
In affected versions of TensorFlow the tf.raw_ops.DataFormatVecPermute API does not validate the src_format and dst_format attributes. The code assumes that these two arguments define a permutation of NHWC. This can result in uninitialized memory accesses, read outside of bounds and even crashes. This is fixed in versions 1.15.5, 2.0.4, 2.1.3, 2.2.2, 2.3.2, and 2.4.0.

## References
- https://github.com/tensorflow/tensorflow/commit/ebc70b7a592420d3d2f359e4b1694c236b82c7ae
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-c9f3-9wfr-wgh7
- https://nvd.nist.gov/vuln/detail/CVE-2020-26267
