# [M] Heap OOB read in TFLite

## Summary
Severity: Medium
Advisory: GHSA-h4pc-gx2w-f2xv
CVE: CVE-2021-29606
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-05-21
Source: https://github.com/advisories/GHSA-h4pc-gx2w-f2xv
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.1.4
- PyPI: `tensorflow` — affected >=2.2.0 <2.2.3
- PyPI: `tensorflow` — affected >=2.3.0 <2.3.3
- PyPI: `tensorflow` — affected >=2.4.0 <2.4.2
- PyPI: `tensorflow-cpu` — affected >=0 <2.1.4
- PyPI: `tensorflow-cpu` — affected >=2.2.0 <2.2.3
- PyPI: `tensorflow-cpu` — affected >=2.3.0 <2.3.3
- PyPI: `tensorflow-cpu` — affected >=2.4.0 <2.4.2
- PyPI: `tensorflow-gpu` — affected >=0 <2.1.4
- PyPI: `tensorflow-gpu` — affected >=2.2.0 <2.2.3
- PyPI: `tensorflow-gpu` — affected >=2.3.0 <2.3.3
- PyPI: `tensorflow-gpu` — affected >=2.4.0 <2.4.2

## Details
### Impact
A specially crafted TFLite model could trigger an OOB read on heap in the TFLite implementation of [`Split_V`](https://github.com/tensorflow/tensorflow/blob/c59c37e7b2d563967da813fa50fe20b21f4da683/tensorflow/lite/kernels/split_v.cc#L99):

```cc
const int input_size = SizeOfDimension(input, axis_value);
``` 

If `axis_value` is not a value between 0 and `NumDimensions(input)`, then the [`SizeOfDimension` function](https://github.com/tensorflow/tensorflow/blob/102b211d892f3abc14f845a72047809b39cc65ab/tensorflow/lite/kernels/kernel_util.h#L148-L150) will access data outside the bounds of the tensor shape array:

```cc
inline int SizeOfDimension(const TfLiteTensor* t, int dim) {
  return t->dims->data[dim];
}
```
  
### Patches 
We have patched the issue in GitHub commit [ae2daeb45abfe2c6dda539cf8d0d6f653d3ef412](https://github.com/tensorflow/tensorflow/commit/ae2daeb45abfe2c6dda539cf8d0d6f653d3ef412).

The fix will be included in TensorFlow 2.5.0. We will also cherrypick this commit on TensorFlow 2.4.2, TensorFlow 2.3.3, TensorFlow 2.2.3 and TensorFlow 2.1.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-h4pc-gx2w-f2xv
- https://nvd.nist.gov/vuln/detail/CVE-2021-29606
- https://github.com/tensorflow/tensorflow/commit/ae2daeb45abfe2c6dda539cf8d0d6f653d3ef412
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-534.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-732.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-243.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/c59c37e7b2d563967da813fa50fe20b21f4da683/tensorflow/lite/kernels/split_v.cc#L99
