# [M] FPE in `tf.raw_ops.UnravelIndex`

## Summary
Severity: Medium
Advisory: GHSA-2wmv-37vq-52g5
CVE: CVE-2021-37668
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-2wmv-37vq-52g5
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
An attacker can cause denial of service in applications serving models using `tf.raw_ops.UnravelIndex` by triggering a division by 0:

```python
import tensorflow as tf

tf.raw_ops.UnravelIndex(indices=-1, dims=[1,0,2])
```
  
The [implementation](https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/core/kernels/unravel_index_op.cc#L36) does not check that the tensor subsumed by `dims` is not empty. Hence, if one element of `dims` is 0, the implementation does a division by 0.

### Patches
We have patched the issue in GitHub commit [a776040a5e7ebf76eeb7eb923bf1ae417dd4d233](https://github.com/tensorflow/tensorflow/commit/a776040a5e7ebf76eeb7eb923bf1ae417dd4d233).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.
  
### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-2wmv-37vq-52g5
- https://nvd.nist.gov/vuln/detail/CVE-2021-37668
- https://github.com/tensorflow/tensorflow/commit/a776040a5e7ebf76eeb7eb923bf1ae417dd4d233
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-581.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-779.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-290.yaml
- https://github.com/tensorflow/tensorflow
