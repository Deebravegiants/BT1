# [H] TensorFlow has Floating Point Exception in TFLite in conv kernel

## Summary
Severity: High
Advisory: GHSA-5w96-866f-6rm8
CVE: CVE-2023-27579
CWE: CWE-697
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-24
Source: https://github.com/advisories/GHSA-5w96-866f-6rm8
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.11.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.11.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.11.1

## Details
### Impact
Constructing a tflite model with a paramater `filter_input_channel` of less than 1 gives a FPE.


### Patches
We have patched the issue in GitHub commit [34f8368c535253f5c9cb3a303297743b62442aaa](https://github.com/tensorflow/tensorflow/commit/34f8368c535253f5c9cb3a303297743b62442aaa).

The fix will be included in TensorFlow 2.12. We will also cherrypick this commit on TensorFlow 2.11.1.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability was reported by Wang Xuan of Qihoo 360 AIVul Team.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-5w96-866f-6rm8
- https://nvd.nist.gov/vuln/detail/CVE-2023-27579
- https://github.com/tensorflow/tensorflow/commit/34f8368c535253f5c9cb3a303297743b62442aaa
- https://github.com/tensorflow/tensorflow
