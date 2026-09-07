# [M] Heap OOB in TFLite

## Summary
Severity: Medium
Advisory: GHSA-c545-c4f9-rf6v
CVE: CVE-2021-37685
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-c545-c4f9-rf6v
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
TFLite's [`expand_dims.cc`](https://github.com/tensorflow/tensorflow/blob/149562d49faa709ea80df1d99fc41d005b81082a/tensorflow/lite/kernels/expand_dims.cc#L36-L50) contains a vulnerability which allows reading one element outside of bounds of heap allocated data:

```cc
  if (axis < 0) { 
    axis = input_dims.size + 1 + axis;
  }   
  TF_LITE_ENSURE(context, axis <= input_dims.size);

  TfLiteIntArray* output_dims = TfLiteIntArrayCreate(input_dims.size + 1);
  for (int i = 0; i < output_dims->size; ++i) {
    if (i < axis) {
      output_dims->data[i] = input_dims.data[i];
    } else if (i == axis) {
      output_dims->data[i] = 1;
    } else {
      output_dims->data[i] = input_dims.data[i - 1];
    }
  }
```

If `axis` is a large negative value (e.g., `-100000`), then after the first `if` it would still be negative. The check following the `if` statement will pass and the `for` loop would read one element before the start of `input_dims.data` (when `i = 0`).

### Patches
We have patched the issue in GitHub commit [d94ffe08a65400f898241c0374e9edc6fa8ed257](https://github.com/tensorflow/tensorflow/commit/d94ffe08a65400f898241c0374e9edc6fa8ed257).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Yakun Zhang of Baidu Security.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-c545-c4f9-rf6v
- https://nvd.nist.gov/vuln/detail/CVE-2021-37685
- https://github.com/tensorflow/tensorflow/commit/d94ffe08a65400f898241c0374e9edc6fa8ed257
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-598.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-796.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-307.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/149562d49faa709ea80df1d99fc41d005b81082a/tensorflow/lite/kernels/expand_dims.cc#L36-L50
