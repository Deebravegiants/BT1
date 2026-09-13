# [H] Null dereference in Grappler's `TrySimplify`

## Summary
Severity: High
Advisory: BIT-tensorflow-2021-29616
Aliases: CVE-2021-29616, GHSA-4hvv-7x94-7vq8, PYSEC-2021-253, PYSEC-2021-544, PYSEC-2021-742
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2021-29616
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.4.0 <2.4.2

## Details
TensorFlow is an end-to-end open source platform for machine learning. The implementation of TrySimplify(https://github.com/tensorflow/tensorflow/blob/c22d88d6ff33031aa113e48aa3fc9aa74ed79595/tensorflow/core/grappler/optimizers/arithmetic_optimizer.cc#L390-L401) has undefined behavior due to dereferencing a null pointer in corner cases that result in optimizing a node with no inputs. The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

## References
- https://github.com/tensorflow/tensorflow/commit/e6340f0665d53716ef3197ada88936c2a5f7a2d3
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-4hvv-7x94-7vq8
- https://nvd.nist.gov/vuln/detail/CVE-2021-29616
