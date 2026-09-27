# [H] BIT-tensorflow-2025-55559

## Summary
Severity: High
Advisory: BIT-tensorflow-2025-55559
Aliases: CVE-2025-55559
Ecosystem: Bitnami
Published: 2025-10-05
Source: https://osv.dev/vulnerability/BIT-tensorflow-2025-55559
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.18.0 <2.18.1

## Details
An issue was discovered TensorFlow v2.18.0. A Denial of Service (DoS) occurs when padding is set to 'valid' in tf.keras.layers.Conv2D.

## References
- https://gist.github.com/shaoyuyoung/0e7d2a586297ae9c8ed14d8706749efc
- https://github.com/tensorflow/tensorflow/issues/84205
- https://nvd.nist.gov/vuln/detail/CVE-2025-55559
