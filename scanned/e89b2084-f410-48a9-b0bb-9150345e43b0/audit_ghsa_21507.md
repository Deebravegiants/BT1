# [M] `tf.raw_ops.Mfcc` crashes

## Summary
Severity: Medium
Advisory: GHSA-rmg2-f698-wq35
CVE: CVE-2022-41896
CWE: CWE-1284, CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-rmg2-f698-wq35
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.8.4
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.8.4
- PyPI: `tensorflow-gpu` — affected >=0 <2.8.4
- PyPI: `tensorflow-cpu` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow-gpu` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow-cpu` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-gpu` — affected >=2.10.0 <2.10.1

## Details
### Impact
If [`ThreadUnsafeUnigramCandidateSampler`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/image/mirror_pad_op.cc) is given input `filterbank_channel_count` greater than the allowed max size, TensorFlow will crash.

```python
import tensorflow as tf
tf.raw_ops.Mfcc(
    spectrogram = [[[1.38, 6.32, 5.75, 9.51]]],
    sample_rate = 2,
    upper_frequency_limit = 5.0,
    lower_frequency_limit = 1.0,
    filterbank_channel_count = 2**31 - 1,
    dct_coefficient_count = 1
)
```

### Patches
We have patched the issue in GitHub commit [39ec7eaf1428e90c37787e5b3fbd68ebd3c48860](https://github.com/tensorflow/tensorflow/commit/39ec7eaf1428e90c37787e5b3fbd68ebd3c48860).

The fix will be included in TensorFlow 2.11. We will also cherrypick this commit on TensorFlow 2.10.1, 2.9.3, and TensorFlow 2.8.4, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Vul AI.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-rmg2-f698-wq35
- https://nvd.nist.gov/vuln/detail/CVE-2022-41896
- https://github.com/tensorflow/tensorflow/commit/39ec7eaf1428e90c37787e5b3fbd68ebd3c48860
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/image/mirror_pad_op.cc
