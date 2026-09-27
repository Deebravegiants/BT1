# [M] Write to immutable memory region in TensorFlow

## Summary
Severity: Medium
Advisory: GHSA-hhvc-g5hv-48c6
CVE: CVE-2020-26268
CWE: CWE-471
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2020-12-10
Source: https://github.com/advisories/GHSA-hhvc-g5hv-48c6
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <1.15.5
- PyPI: `tensorflow` — affected >=2.0.0 <2.0.4
- PyPI: `tensorflow` — affected >=2.1.0 <2.1.3
- PyPI: `tensorflow` — affected >=2.2.0 <2.2.2
- PyPI: `tensorflow` — affected >=2.3.0 <2.3.2
- PyPI: `tensorflow-cpu` — affected >=0 <1.15.5
- PyPI: `tensorflow-cpu` — affected >=2.0.0 <2.0.4
- PyPI: `tensorflow-cpu` — affected >=2.1.0 <2.1.3
- PyPI: `tensorflow-cpu` — affected >=2.2.0 <2.2.2
- PyPI: `tensorflow-cpu` — affected >=2.3.0 <2.3.2
- PyPI: `tensorflow-gpu` — affected >=0 <1.15.5
- PyPI: `tensorflow-gpu` — affected >=2.0.0 <2.0.4
- PyPI: `tensorflow-gpu` — affected >=2.1.0 <2.1.3
- PyPI: `tensorflow-gpu` — affected >=2.2.0 <2.2.2
- PyPI: `tensorflow-gpu` — affected >=2.3.0 <2.3.2

## Details
### Impact
The `tf.raw_ops.ImmutableConst` operation returns a constant tensor created from a memory mapped file which is assumed immutable. However, if the type of the tensor is not an integral type, the operation crashes the Python interpreter as it tries to write to the memory area:

```python
>>> import tensorflow as tf
>>> with open('/tmp/test.txt','w') as f: f.write('a'*128)
>>> tf.raw_ops.ImmutableConst(dtype=tf.string,shape=2,
                              memory_region_name='/tmp/test.txt')
```

If the file is too small, TensorFlow properly returns an error as the memory area has fewer bytes than what is needed for the tensor it creates. However, as soon as there are enough bytes, the above snippet causes a segmentation fault.

This is because the alocator used to return the buffer data is not marked as returning an opaque handle since the [needed virtual method](https://github.com/tensorflow/tensorflow/blob/c1e1fc899ad5f8c725dcbb6470069890b5060bc7/tensorflow/core/framework/typed_allocator.h#L78-L85) is [not overriden](https://github.com/tensorflow/tensorflow/blob/acdf3c04fcfa767ae8d109b9e1f727ef050dba4d/tensorflow/core/kernels/immutable_constant_op.cc).

### Patches
We have patched the issue in GitHub commit [c1e1fc899ad5f8c725dcbb6470069890b5060bc7](https://github.com/tensorflow/tensorflow/commit/c1e1fc899ad5f8c725dcbb6470069890b5060bc7) and will release TensorFlow 2.4.0 containing the patch. TensorFlow nightly packages after this commit will also have the issue resolved.

Since this issue also impacts TF versions before 2.4, we will patch all releases between 1.15 and 2.3 inclusive.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-hhvc-g5hv-48c6
- https://nvd.nist.gov/vuln/detail/CVE-2020-26268
- https://github.com/tensorflow/tensorflow/commit/c1e1fc899ad5f8c725dcbb6470069890b5060bc7
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-299.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-334.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-255.yaml
- https://github.com/tensorflow/tensorflow
