# [M] Data leak in Tensorflow

## Summary
Severity: Medium
Advisory: GHSA-g7p5-5759-qv46
CVE: CVE-2020-15205
CWE: CWE-119, CWE-122, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2020-09-25
Source: https://github.com/advisories/GHSA-g7p5-5759-qv46
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <1.15.4
- PyPI: `tensorflow` — affected >=2.0.0 <2.0.3
- PyPI: `tensorflow` — affected >=2.1.0 <2.1.2
- PyPI: `tensorflow` — affected >=2.2.0 <2.2.1
- PyPI: `tensorflow` — affected >=2.3.0 <2.3.1
- PyPI: `tensorflow-cpu` — affected >=0 <1.15.4
- PyPI: `tensorflow-cpu` — affected >=2.0.0 <2.0.3
- PyPI: `tensorflow-cpu` — affected >=2.1.0 <2.1.2
- PyPI: `tensorflow-cpu` — affected >=2.2.0 <2.2.1
- PyPI: `tensorflow-cpu` — affected >=2.3.0 <2.3.1
- PyPI: `tensorflow-gpu` — affected >=0 <1.15.4
- PyPI: `tensorflow-gpu` — affected >=2.0.0 <2.0.3
- PyPI: `tensorflow-gpu` — affected >=2.1.0 <2.1.2
- PyPI: `tensorflow-gpu` — affected >=2.2.0 <2.2.1
- PyPI: `tensorflow-gpu` — affected >=2.3.0 <2.3.1

## Details
### Impact
The `data_splits` argument of [`tf.raw_ops.StringNGrams`](https://www.tensorflow.org/api_docs/python/tf/raw_ops/StringNGrams) lacks validation. This allows a user to pass values that can cause heap overflow errors and even leak contents of memory
```python
>>> tf.raw_ops.StringNGrams(data=["aa", "bb", "cc", "dd", "ee", "ff"], data_splits=[0,8], separator=" ", ngram_widths=[3], left_pad="", right_pad="", pad_width=0, preserve_short_sequences=False)
StringNGrams(ngrams=<tf.Tensor: shape=(6,), dtype=string, numpy=
array([b'aa bb cc', b'bb cc dd', b'cc dd ee', b'dd ee ff',
       b'ee ff \xf4j\xa7q\x7f\x00\x00q\x00\x00\x00\x00\x00\x00\x00\xd8\x9b~\xa8q\x7f\x00',
       b'ff \xf4j\xa7q\x7f\x00\x00q\x00\x00\x00\x00\x00\x00\x00\xd8\x9b~\xa8q\x7f\x00 \x9b~\xa8q\x7f\x00\x00p\xf5j\xa7q\x7f\x00\x00H\xf8j\xa7q\x7f\x00\x00\xf0\xf3\xf7\x85q\x7f\x00\x00`}\xa6\x00\x00\x00\x00\x00`~\xa6\x00\x00\x00\x00\x00\xb0~\xeb\x9bq\x7f\x00'],...
```

All the binary strings after `ee ff` are contents from the memory stack. Since these can contain return addresses, this data leak can be used to defeat ASLR.

### Patches
We have patched the issue in 0462de5b544ed4731aa2fb23946ac22c01856b80 and will release patch releases for all versions between 1.15 and 2.3.

We recommend users to upgrade to TensorFlow 1.15.4, 2.0.3, 2.1.2, 2.2.1, or 2.3.1.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-g7p5-5759-qv46
- https://nvd.nist.gov/vuln/detail/CVE-2020-15205
- https://github.com/tensorflow/tensorflow/commit/0462de5b544ed4731aa2fb23946ac22c01856b80
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-285.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-320.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-128.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.3.1
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00065.html
