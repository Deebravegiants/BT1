# [H] Heap OOB in `ResourceScatterUpdate`

## Summary
Severity: High
Advisory: GHSA-7fvx-3jfc-2cpc
CVE: CVE-2021-37655
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-7fvx-3jfc-2cpc
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
An attacker can trigger a read from outside of bounds of heap allocated data by sending invalid arguments to `tf.raw_ops.ResourceScatterUpdate`:

```python
import tensorflow as tf

v = tf.Variable([b'vvv'])
tf.raw_ops.ResourceScatterUpdate(
  resource=v.handle,
  indices=[0],
  updates=['1', '2', '3', '4', '5'])
```
  
The [implementation](https://github.com/tensorflow/tensorflow/blob/f24faa153ad31a4b51578f8181d3aaab77a1ddeb/tensorflow/core/kernels/resource_variable_ops.cc#L919-L923) has an incomplete validation of the relationship between the shapes of `indices` and `updates`: instead of checking that the shape of `indices` is a prefix of the shape of `updates` (so that broadcasting can happen), code only checks that the number of elements in these two tensors are in a divisibility relationship.

### Patches 
We have patched the issue in GitHub commit [01cff3f986259d661103412a20745928c727326f](https://github.com/tensorflow/tensorflow/commit/01cff3f986259d661103412a20745928c727326f).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.
    
### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.
    
### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-7fvx-3jfc-2cpc
- https://nvd.nist.gov/vuln/detail/CVE-2021-37655
- https://github.com/tensorflow/tensorflow/commit/01cff3f986259d661103412a20745928c727326f
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-568.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-766.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-277.yaml
- https://github.com/tensorflow/tensorflow
