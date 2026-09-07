# [H] Access to invalid memory during shape inference in `Cudnn*` ops

## Summary
Severity: High
Advisory: GHSA-cqv6-3phm-hcwx
CVE: CVE-2021-41221
CWE: CWE-120, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-cqv6-3phm-hcwx
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
The [shape inference code](https://github.com/tensorflow/tensorflow/blob/9ff27787893f76d6971dcd1552eb5270d254f31b/tensorflow/core/ops/cudnn_rnn_ops.cc) for the `Cudnn*` operations in TensorFlow can be tricked into accessing invalid memory, via a heap buffer overflow:

```python
import tensorflow as tf

@tf.function
def func():
  return tf.raw_ops.CudnnRNNV3(
    input=[0.1, 0.1],
    input_h=[0.5],
    input_c=[0.1, 0.1, 0.1], 
    params=[0.5, 0.5],
    sequence_lengths=[-1, 0, 1])
  
func() 
```
  
This occurs because the ranks of the `input`, `input_h` and `input_c` parameters are not validated, but code assumes they have certain values:

```cc
auto input_shape = c->input(0);
auto input_h_shape = c->input(1);
auto seq_length = c->Dim(input_shape, 0);
auto batch_size = c->Dim(input_shape, 1);  // assumes rank >= 2
auto num_units = c->Dim(input_h_shape, 2); // assumes rank >= 3
``` 

### Patches
We have patched the issue in GitHub commit [af5fcebb37c8b5d71c237f4e59c6477015c78ce6](https://github.com/tensorflow/tensorflow/commit/af5fcebb37c8b5d71c237f4e59c6477015c78ce6).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-cqv6-3phm-hcwx
- https://nvd.nist.gov/vuln/detail/CVE-2021-41221
- https://github.com/tensorflow/tensorflow/commit/af5fcebb37c8b5d71c237f4e59c6477015c78ce6
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-630.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-828.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-413.yaml
- https://github.com/tensorflow/tensorflow
