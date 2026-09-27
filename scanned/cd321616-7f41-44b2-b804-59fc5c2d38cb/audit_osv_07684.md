# [M] BIT-tensorflow-2025-55556

## Summary
Severity: Medium
Advisory: BIT-tensorflow-2025-55556
Aliases: CVE-2025-55556
Ecosystem: Bitnami
Published: 2025-10-05
Source: https://osv.dev/vulnerability/BIT-tensorflow-2025-55556
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.18.0 <2.18.1

## Details
TensorFlow v2.18.0 was discovered to output random results when compiling Embedding, leading to unexpected behavior in the application.

## References
- https://gist.github.com/shaoyuyoung/0e7d2a586297ae9c8ed14d8706749efc
- https://github.com/tensorflow/tensorflow/issues/82317
- https://nvd.nist.gov/vuln/detail/CVE-2025-55556
