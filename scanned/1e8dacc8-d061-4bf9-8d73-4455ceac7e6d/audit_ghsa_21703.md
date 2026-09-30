# [H] Overflow and uncaught divide by zero in Tensorflow

## Summary
Severity: High
Advisory: GHSA-34f9-hjfq-rr8j
CVE: CVE-2022-21729
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-34f9-hjfq-rr8j
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.5.3
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow` — affected >=2.7.0 <2.7.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.5.3
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow-cpu` — affected >=2.7.0 <2.7.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.5.3
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow-gpu` — affected >=2.7.0 <2.7.1

## Details
### Impact 
The [implementation of `UnravelIndex`](https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/unravel_index_op.cc#L36-L135) is vulnerable to a division by zero caused by an integer overflow bug:

```python
import tensorflow as tf

tf.raw_ops.UnravelIndex(indices=-0x100000,dims=[0x100000,0x100000])
```

### Patches
We have patched the issue in GitHub commit [58b34c6c8250983948b5a781b426f6aa01fd47af](https://github.com/tensorflow/tensorflow/commit/58b34c6c8250983948b5a781b426f6aa01fd47af).
    
The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.
    
### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.
    
### Attribution
This vulnerability has been reported by Yu Tian of Qihoo 360 AIVul Team.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-34f9-hjfq-rr8j
- https://nvd.nist.gov/vuln/detail/CVE-2022-21729
- https://github.com/tensorflow/tensorflow/commit/58b34c6c8250983948b5a781b426f6aa01fd47af
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-53.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-108.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/unravel_index_op.cc#L36-L135
