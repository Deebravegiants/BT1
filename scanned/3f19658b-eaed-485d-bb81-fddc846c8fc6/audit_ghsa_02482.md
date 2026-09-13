# [H] Reference binding to nullptr in map operations

## Summary
Severity: High
Advisory: GHSA-qr82-2c78-4m8h
CVE: CVE-2021-37671
CWE: CWE-824
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-qr82-2c78-4m8h
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
An attacker can cause undefined behavior via binding a reference to null pointer in `tf.raw_ops.Map*` and `tf.raw_ops.OrderedMap*` operations:

```python
import tensorflow as tf
  
tf.raw_ops.MapPeek(
  key=tf.constant([8],dtype=tf.int64),
  indices=[],
  dtypes=[tf.int32],
  capacity=8,
  memory_limit=128)
```

The [implementation](https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/core/kernels/map_stage_op.cc#L222-L248) has a check in place to ensure that `indices` is in ascending order, but does not check that `indices` is not empty.
    
### Patches
We have patched the issue in GitHub commit [532f5c5a547126c634fefd43bbad1dc6417678ac](https://github.com/tensorflow/tensorflow/commit/532f5c5a547126c634fefd43bbad1dc6417678ac).
                       
The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.
    
### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-qr82-2c78-4m8h
- https://nvd.nist.gov/vuln/detail/CVE-2021-37671
- https://github.com/tensorflow/tensorflow/commit/532f5c5a547126c634fefd43bbad1dc6417678ac
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-584.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-782.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-293.yaml
- https://github.com/tensorflow/tensorflow
