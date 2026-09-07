# [H] Integer overflow in TFLite array creation

## Summary
Severity: High
Advisory: GHSA-9gwq-6cwj-47h3
CVE: CVE-2022-23558
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-9gwq-6cwj-47h3
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
An attacker can craft a TFLite model that would cause an integer overflow [in `TfLiteIntArrayCreate`](https://github.com/tensorflow/tensorflow/blob/ca6f96b62ad84207fbec580404eaa7dd7403a550/tensorflow/lite/c/common.c#L53-L60):

```cc
TfLiteIntArray* TfLiteIntArrayCreate(int size) {
  int alloc_size = TfLiteIntArrayGetSizeInBytes(size);
  // ...
  TfLiteIntArray* ret = (TfLiteIntArray*)malloc(alloc_size);
  // ...
} 
```

The [`TfLiteIntArrayGetSizeInBytes`](https://github.com/tensorflow/tensorflow/blob/ca6f96b62ad84207fbec580404eaa7dd7403a550/tensorflow/lite/c/common.c#L24-L33) returns an `int` instead of a `size_t`:

```cc
int TfLiteIntArrayGetSizeInBytes(int size) {
  static TfLiteIntArray dummy;

  int computed_size = sizeof(dummy) + sizeof(dummy.data[0]) * size;
#if defined(_MSC_VER)
  // Context for why this is needed is in http://b/189926408#comment21
  computed_size -= sizeof(dummy.data[0]);
#endif
  return computed_size;
}
```

An attacker can control model inputs such that `computed_size` overflows the size of `int` datatype.

### Patches
We have patched the issue in GitHub commit [a1e1511dde36b3f8aa27a6ec630838e7ea40e091](https://github.com/tensorflow/tensorflow/commit/a1e1511dde36b3f8aa27a6ec630838e7ea40e091).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Wang Xuan of Qihoo 360 AIVul Team.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-9gwq-6cwj-47h3
- https://nvd.nist.gov/vuln/detail/CVE-2022-23558
- https://github.com/tensorflow/tensorflow/commit/a1e1511dde36b3f8aa27a6ec630838e7ea40e091
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-67.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-122.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/ca6f96b62ad84207fbec580404eaa7dd7403a550/tensorflow/lite/c/common.c#L24-L33
- https://github.com/tensorflow/tensorflow/blob/ca6f96b62ad84207fbec580404eaa7dd7403a550/tensorflow/lite/c/common.c#L53-L60
