# [H] FractionalMaxPool and FractionalAVGPool heap out-of-bounds acess

## Summary
Severity: High
Advisory: GHSA-xvwp-h6jv-7472
CVE: CVE-2022-41900
CWE: CWE-125, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-xvwp-h6jv-7472
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.8.4
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.8.4
- PyPI: `tensorflow-gpu` — affected >=0 <2.8.4
- PyPI: `tensorflow-cpu` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow-gpu` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow-cpu` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-gpu` — affected >=2.10.0 <2.10.1

## Details
### Impact
An input `pooling_ratio` that is smaller than 1 will trigger a heap OOB in [`tf.raw_ops.FractionalMaxPool`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/fractional_max_pool_op.cc) and [`tf.raw_ops.FractionalAvgPool`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/fractional_avg_pool_op.cc).

### Patches
We have patched the issue in GitHub commit [216525144ee7c910296f5b05d214ca1327c9ce48](https://github.com/tensorflow/tensorflow/commit/216525144ee7c910296f5b05d214ca1327c9ce48).

The fix will be included in TensorFlow 2.11.0. We will also cherry pick this commit on TensorFlow 2.10.1.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-xvwp-h6jv-7472
- https://nvd.nist.gov/vuln/detail/CVE-2022-41900
- https://github.com/tensorflow/tensorflow/commit/216525144ee7c910296f5b05d214ca1327c9ce48
- https://github.com/tensorflow/tensorflow
