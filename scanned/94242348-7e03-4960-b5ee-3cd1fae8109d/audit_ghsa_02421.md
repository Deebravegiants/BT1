# [H] Heap buffer overflow in `FractionalAvgPoolGrad`

## Summary
Severity: High
Advisory: GHSA-hpv4-7p9c-mvfr
CVE: CVE-2021-37651
CWE: CWE-125, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-hpv4-7p9c-mvfr
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.3.4
- PyPI: `tensorflow` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.3.4
- PyPI: `tensorflow-cpu` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.3.4
- PyPI: `tensorflow-gpu` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.1

## Details
### Impact
The implementation for `tf.raw_ops.FractionalAvgPoolGrad` can be tricked into accessing data outside of bounds of heap allocated buffers:

```python
import tensorflow as tf

tf.raw_ops.FractionalAvgPoolGrad(
  orig_input_tensor_shape=[0,1,2,3],
  out_backprop = np.array([[[[541],[541]],[[541],[541]]]]),
  row_pooling_sequence=[0, 0, 0, 0, 0],
  col_pooling_sequence=[-2, 0, 0, 2, 0],
  overlapping=True)
```

The [implementation](https://github.com/tensorflow/tensorflow/blob/f24faa153ad31a4b51578f8181d3aaab77a1ddeb/tensorflow/core/kernels/fractional_avg_pool_op.cc#L205) does not validate that the input tensor is non-empty. Thus, code constructs an empty `EigenDoubleMatrixMap` and then accesses this buffer with indices that are outside of the empty area.

### Patches
We have patched the issue in GitHub commit [0f931751fb20f565c4e94aa6df58d54a003cdb30](https://github.com/tensorflow/tensorflow/commit/0f931751fb20f565c4e94aa6df58d54a003cdb30).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-hpv4-7p9c-mvfr
- https://nvd.nist.gov/vuln/detail/CVE-2021-37651
- https://github.com/tensorflow/tensorflow/commit/0f931751fb20f565c4e94aa6df58d54a003cdb30
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-564.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-762.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-273.yaml
- https://github.com/tensorflow/tensorflow
