# [H] TensorFlow vulnerable to Out-of-Bounds Read in DynamicStitch

## Summary
Severity: High
Advisory: GHSA-93vr-9q9m-pj8p
CVE: CVE-2023-25659
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-24
Source: https://github.com/advisories/GHSA-93vr-9q9m-pj8p
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.11.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.11.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.11.1

## Details
### Impact
If the parameter `indices` for `DynamicStitch` does not match the shape of the parameter `data`, it can trigger an stack OOB read.

```python
import tensorflow as tf
func = tf.raw_ops.DynamicStitch
para={'indices': [[0xdeadbeef], [405], [519], [758], [1015]], 'data': [[110.27793884277344], [120.29475402832031], [157.2418212890625], [157.2626953125], [188.45382690429688]]}
y = func(**para)
```

### Patches
We have patched the issue in GitHub commit [ee004b18b976eeb5a758020af8880236cd707d05](https://github.com/tensorflow/tensorflow/commit/ee004b18b976eeb5a758020af8880236cd707d05).

The fix will be included in TensorFlow 2.12. We will also cherrypick this commit on TensorFlow 2.11.1.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This has been reported via Google OSS VRP.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-93vr-9q9m-pj8p
- https://nvd.nist.gov/vuln/detail/CVE-2023-25659
- https://github.com/tensorflow/tensorflow/commit/ee004b18b976eeb5a758020af8880236cd707d05
- https://github.com/tensorflow/tensorflow
