# [C] OOB read in `Gather_nd` op in TensorFlow Lite Micro

## Summary
Severity: Critical
Advisory: BIT-tensorflow-2022-35938
Aliases: CVE-2022-35938, GHSA-3m3g-pf5v-5hpj
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tensorflow-2022-35938
Type: osv

## Affected
- Bitnami: `tensorflow` — affected >=2.9.0 <2.9.1

## Details
TensorFlow is an open source platform for machine learning. The `GatherNd` function takes arguments that determine the sizes of inputs and outputs. If the inputs given are greater than or equal to the sizes of the outputs, an out-of-bounds memory read or a crash is triggered. This issue has been patched in GitHub commit 4142e47e9e31db481781b955ed3ff807a781b494. The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range. There are no known workarounds for this issue.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-3m3g-pf5v-5hpj
- https://github.com/tensorflow/tflite-micro/blob/1bc98621180a350eb4e8d3318ea8e228c7559b37/tensorflow/lite/micro/kernels/gather_nd.cc#L143-L154
- https://github.com/tensorflow/tflite-micro/commit/4142e47e9e31db481781b955ed3ff807a781b494
- https://nvd.nist.gov/vuln/detail/CVE-2022-35938
