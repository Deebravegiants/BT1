# [H] Out of bounds read and write in Tensorflow

## Summary
Severity: High
Advisory: GHSA-77gp-3h4r-6428
CVE: CVE-2022-23574
CWE: CWE-125, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-77gp-3h4r-6428
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
There is a typo in TensorFlow's [`SpecializeType`](https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/framework/full_type_util.cc#L81-L102) which results in heap OOB read/write:

```cc
for (int i = 0; i < op_def.output_arg_size(); i++) {
  // ...
  for (int j = 0; j < t->args_size(); j++) {
    auto* arg = t->mutable_args(i);
    // ...
  }
} 
```

Due to a typo, `arg` is initialized to the `i`th mutable argument in a loop where the loop index is `j`. Hence it is possible to assign to `arg` from outside the vector of arguments. Since this is a mutable proto value, it allows both read and write to outside of bounds data.

### Patches
We have patched the issue in GitHub commit [0657c83d08845cc434175934c642299de2c0f042](https://github.com/tensorflow/tensorflow/commit/0657c83d08845cc434175934c642299de2c0f042).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, and TensorFlow 2.6.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-77gp-3h4r-6428
- https://nvd.nist.gov/vuln/detail/CVE-2022-23574
- https://github.com/tensorflow/tensorflow/commit/0657c83d08845cc434175934c642299de2c0f042
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-83.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-138.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/framework/full_type_util.cc#L81-L102
