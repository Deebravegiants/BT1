# [M] FPE in LSH in TFLite

## Summary
Severity: Medium
Advisory: GHSA-27qf-jwm8-g7f3
CVE: CVE-2021-37691
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-27qf-jwm8-g7f3
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
An attacker can craft a TFLite model that would trigger a division by zero error in LSH  [implementation](https://github.com/tensorflow/tensorflow/blob/149562d49faa709ea80df1d99fc41d005b81082a/tensorflow/lite/kernels/lsh_projection.cc#L118).

```cc
int RunningSignBit(const TfLiteTensor* input, const TfLiteTensor* weight,
                   float seed) {
  int input_item_bytes = input->bytes / SizeOfDimension(input, 0);
  // ...
}
```
          
There is no check that the first dimension of the input is non zero.
      
### Patches
We have patched the issue in GitHub commit [0575b640091680cfb70f4dd93e70658de43b94f9](https://github.com/tensorflow/tensorflow/commit/0575b640091680cfb70f4dd93e70658de43b94f9).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick thiscommit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for  more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Yakun Zhang of Baidu Security.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-27qf-jwm8-g7f3
- https://nvd.nist.gov/vuln/detail/CVE-2021-37691
- https://github.com/tensorflow/tensorflow/commit/0575b640091680cfb70f4dd93e70658de43b94f9
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-604.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-802.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-313.yaml
- https://github.com/tensorflow/tensorflow
