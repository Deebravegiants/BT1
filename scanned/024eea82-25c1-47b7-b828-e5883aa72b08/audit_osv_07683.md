# [C] TensorFlow vulnerable to Heap Buffer Overflow in AvgPoolGrad

## Summary
Severity: Critical
Advisory: BIT-tensorflow-2023-25664
Aliases: CVE-2023-25664, GHSA-6hg6-5c2q-7rcr, PYSEC-2026-1951, PYSEC-2026-3122
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2023-25664
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=0 <2.12.0

## Details
TensorFlow is an open source platform for machine learning. Prior to versions 2.12.0 and 2.11.1, there is a heap buffer overflow in TAvgPoolGrad. A fix is included in TensorFlow 2.12.0 and 2.11.1.

## References
- https://github.com/tensorflow/tensorflow/commit/ddaac2bdd099bec5d7923dea45276a7558217e5b
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-6hg6-5c2q-7rcr
- https://nvd.nist.gov/vuln/detail/CVE-2023-25664
