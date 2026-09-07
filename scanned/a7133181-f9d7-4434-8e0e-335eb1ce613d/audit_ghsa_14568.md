# [H] TensorFlow has Null Pointer Error in LookupTableImportV2

## Summary
Severity: High
Advisory: GHSA-94mm-g2mv-8p7r
CVE: CVE-2023-25672
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-24
Source: https://github.com/advisories/GHSA-94mm-g2mv-8p7r
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.11.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.11.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.11.1

## Details
### Impact
The function `tf.raw_ops.LookupTableImportV2` cannot handle scalars in the `values` parameter and gives an NPE.

```python
import tensorflow as tf

v = tf.Variable(1)

@tf.function(jit_compile=True)
def test():
   func = tf.raw_ops.LookupTableImportV2
   para={'table_handle': v.handle,'keys': [62.98910140991211, 94.36528015136719], 'values': -919}

   y = func(**para)
   return y

print(test())
```

### Patches
We have patched the issue in GitHub commit [980b22536abcbbe1b4a5642fc940af33d8c19b69](https://github.com/tensorflow/tensorflow/commit/980b22536abcbbe1b4a5642fc940af33d8c19b69).

The fix will be included in TensorFlow 2.12. We will also cherrypick this commit on TensorFlow 2.11.1.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by r3pwnx of 360 AIVul Team

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-94mm-g2mv-8p7r
- https://nvd.nist.gov/vuln/detail/CVE-2023-25672
- https://github.com/tensorflow/tensorflow/commit/980b22536abcbbe1b4a5642fc940af33d8c19b69
- https://github.com/tensorflow/tensorflow
