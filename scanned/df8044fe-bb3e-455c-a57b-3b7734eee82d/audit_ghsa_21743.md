# [H] Integer overflow in TFLite

## Summary
Severity: High
Advisory: GHSA-98p5-x8x4-c9m5
CVE: CVE-2022-23559
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-98p5-x8x4-c9m5
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
An attacker can craft a TFLite model that would cause an integer overflow [in embedding lookup operations](https://github.com/tensorflow/tensorflow/blob/ca6f96b62ad84207fbec580404eaa7dd7403a550/tensorflow/lite/kernels/embedding_lookup_sparse.cc#L179-L189):

```cc
  int embedding_size = 1;
  int lookup_size = 1;
  for (int i = 0; i < lookup_rank - 1; i++, k++) {
    const int dim = dense_shape->data.i32[i];
    lookup_size *= dim;
    output_shape->data[k] = dim;
  }
  for (int i = 1; i < embedding_rank; i++, k++) {
    const int dim = SizeOfDimension(value, i);
    embedding_size *= dim;
    output_shape->data[k] = dim;
  } 
```

Both `embedding_size` and `lookup_size` are products of values provided by the user. Hence, a malicious user could trigger overflows in the multiplication.

In certain scenarios, this can then result in heap OOB read/write.
  
### Patches
We have patched the issue in GitHub commits [f19be71717c497723ba0cea0379e84f061a75e01](https://github.com/tensorflow/tensorflow/commit/f19be71717c497723ba0cea0379e84f061a75e01), [1de49725a5fc4e48f1a3b902ec3599ee99283043](https://github.com/tensorflow/tensorflow/commit/1de49725a5fc4e48f1a3b902ec3599ee99283043) and [a4e401da71458d253b05e41f28637b65baf64be4](https://github.com/tensorflow/tensorflow/commit/a4e401da71458d253b05e41f28637b65baf64be4).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Wang Xuan of Qihoo 360 AIVul Team.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-98p5-x8x4-c9m5
- https://nvd.nist.gov/vuln/detail/CVE-2022-23559
- https://github.com/tensorflow/tensorflow/commit/1de49725a5fc4e48f1a3b902ec3599ee99283043
- https://github.com/tensorflow/tensorflow/commit/a4e401da71458d253b05e41f28637b65baf64be4
- https://github.com/tensorflow/tensorflow/commit/f19be71717c497723ba0cea0379e84f061a75e01
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-68.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-123.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/ca6f96b62ad84207fbec580404eaa7dd7403a550/tensorflow/lite/kernels/embedding_lookup_sparse.cc#L179-L189
