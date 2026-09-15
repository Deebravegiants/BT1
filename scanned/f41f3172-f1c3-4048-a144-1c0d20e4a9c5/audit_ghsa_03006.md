# [H] Heap OOB read in `tf.raw_ops.SparseCountSparseOutput`

## Summary
Severity: High
Advisory: GHSA-m342-ff57-4jcc
CVE: CVE-2021-41210
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-m342-ff57-4jcc
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow` — affected >=0 <2.4.4
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-cpu` — affected >=0 <2.4.4
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-gpu` — affected >=0 <2.4.4

## Details
### Impact
The [shape inference functions for `SparseCountSparseOutput`](https://github.com/tensorflow/tensorflow/blob/e0b6e58c328059829c3eb968136f17aa72b6c876/tensorflow/core/ops/count_ops.cc#L43-L50) can trigger a read outside of bounds of heap allocated array:

```python
import tensorflow as tf

@tf.function
def func():
  return tf.raw_ops.SparseCountSparseOutput(
    indices=[1],
    values=[[1]],
    dense_shape=[10],
    weights=[],
    binary_output= True)

func()
```

The function fails to check that the first input (i.e., `indices`) has rank 2:

```cc
  auto rank = c->Dim(c->input(0), 1);
```

### Patches
We have patched the issue in GitHub commit [701cfaca222a82afbeeb17496bd718baa65a67d2](https://github.com/tensorflow/tensorflow/commit/701cfaca222a82afbeeb17496bd718baa65a67d2).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-m342-ff57-4jcc
- https://nvd.nist.gov/vuln/detail/CVE-2021-41210
- https://github.com/tensorflow/tensorflow/commit/701cfaca222a82afbeeb17496bd718baa65a67d2
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-619.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-817.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-402.yaml
- https://github.com/tensorflow/tensorflow
