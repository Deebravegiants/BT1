# [M] `std::abort` raised from `TensorListReserve`

## Summary
Severity: Medium
Advisory: GHSA-27j5-4p9v-pp67
CVE: CVE-2021-37644
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-27j5-4p9v-pp67
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
Providing a negative element to `num_elements` list argument of  `tf.raw_ops.TensorListReserve` causes the runtime to abort the process due to reallocating a `std::vector` to have a negative number of elements:

```python
import tensorflow as tf

tf.raw_ops.TensorListReserve(
  element_shape = tf.constant([1]),
  num_elements=tf.constant([-1]),
  element_dtype = tf.int32)
```

The [implementation](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/kernels/list_kernels.cc#L312) calls `std::vector.resize()` with the new size controlled by input given by the user, without checking that this input is valid.

### Patches
We have patched the issue in GitHub commit [8a6e874437670045e6c7dc6154c7412b4a2135e2](https://github.com/tensorflow/tensorflow/commit/8a6e874437670045e6c7dc6154c7412b4a2135e2).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information 
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-27j5-4p9v-pp67
- https://nvd.nist.gov/vuln/detail/CVE-2021-37644
- https://github.com/tensorflow/tensorflow/commit/8a6e874437670045e6c7dc6154c7412b4a2135e2
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-557.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-755.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-266.yaml
- https://github.com/tensorflow/tensorflow
