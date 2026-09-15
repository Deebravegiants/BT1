# [M] Bad alloc in `StringNGrams` caused by integer conversion

## Summary
Severity: Medium
Advisory: GHSA-h6jh-7gv5-28vg
CVE: CVE-2021-37646
CWE: CWE-681
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-h6jh-7gv5-28vg
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
The implementation of `tf.raw_ops.StringNGrams` is vulnerable to an integer overflow issue caused by converting a signed integer value to an unsigned one and then allocating memory based on this value.

```python
import tensorflow as tf

tf.raw_ops.StringNGrams(
  data=['',''],
  data_splits=[0,2],
  separator=' '*100,
  ngram_widths=[-80,0,0,-60],
  left_pad=' ',
  right_pad=' ',
  pad_width=100,
  preserve_short_sequences=False)
```

The [implementation](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/kernels/string_ngrams_op.cc#L184) calls `reserve` on a `tstring` with a value that sometimes can be negative if user supplies negative `ngram_widths`. The `reserve` method calls `TF_TString_Reserve` which has an `unsigned long` argument for the size of the buffer. Hence, the implicit conversion transforms the negative value to a large integer.

### Patches
We have patched the issue in GitHub commit [c283e542a3f422420cfdb332414543b62fc4e4a5](https://github.com/tensorflow/tensorflow/commit/c283e542a3f422420cfdb332414543b62fc4e4a5).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-h6jh-7gv5-28vg
- https://nvd.nist.gov/vuln/detail/CVE-2021-37646
- https://github.com/tensorflow/tensorflow/commit/c283e542a3f422420cfdb332414543b62fc4e4a5
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-559.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-757.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-268.yaml
- https://github.com/tensorflow/tensorflow
