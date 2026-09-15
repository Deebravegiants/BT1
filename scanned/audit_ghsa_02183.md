# [H] Incorrect validation of `SaveV2` inputs

## Summary
Severity: High
Advisory: GHSA-wp77-4gmm-7cq8
CVE: CVE-2021-37648
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-wp77-4gmm-7cq8
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
The code for `tf.raw_ops.SaveV2` does not properly validate the inputs and an attacker can trigger a null pointer dereference:

```python
import tensorflow as tf

tf.raw_ops.SaveV2(
  prefix=['tensorflow'],
  tensor_name=['v'],
  shape_and_slices=[],
  tensors=[1,2,3])
```
  
The [implementation](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/kernels/save_restore_v2_ops.cc) uses `ValidateInputs` to  check that the input arguments are valid. This validation would have caught the illegal state represented by the reproducer  above.

However, the validation uses `OP_REQUIRES` which translates to setting the `Status` object of the current `OpKernelContext` to an error status, followed by an empty `return` statement which just terminates the execution of the function it is present in. However, this does not mean that the kernel execution is finalized: instead, execution continues from the next line in `Compute` that follows the call to `ValidateInputs`. This is equivalent to lacking the validation.
      
### Patches
We have patched the issue in GitHub commit [9728c60e136912a12d99ca56e106b7cce7af5986](https://github.com/tensorflow/tensorflow/commit/9728c60e136912a12d99ca56e106b7cce7af5986).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.                                                                                                                                                                                                                                               

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-wp77-4gmm-7cq8
- https://nvd.nist.gov/vuln/detail/CVE-2021-37648
- https://github.com/tensorflow/tensorflow/commit/9728c60e136912a12d99ca56e106b7cce7af5986
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-561.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-759.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-270.yaml
- https://github.com/tensorflow/tensorflow
