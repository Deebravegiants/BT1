# [H] Null pointer dereference in TFLite MLIR optimizations

## Summary
Severity: High
Advisory: GHSA-wf5p-c75w-w3wh
CVE: CVE-2021-37689
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-wf5p-c75w-w3wh
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
An attacker can craft a TFLite model that would trigger a null pointer dereference, which would result in a crash and denial of service:

This is caused by the MLIR optimization of `L2NormalizeReduceAxis` operator. The [implementation](https://github.com/tensorflow/tensorflow/blob/149562d49faa709ea80df1d99fc41d005b81082a/tensorflow/compiler/mlir/lite/transforms/optimize.cc#L67-L70) unconditionally dereferences a pointer to an iterator to a vector without checking that the vector has elements:

```cc
bool L2NormalizeReduceAxis(Value sq_op, DenseElementsAttr axis) {
  if (sq_op.getType().cast<ShapedType>().getRank() - 1 ==
          *axis.getValues<int>().begin() ||
      *axis.getValues<int>().begin() == -1) {
      // ...
  }
  // ...
}
```

### Patches
We have patched the issue in GitHub commit [d6b57f461b39fd1aa8c1b870f1b974aac3554955](https://github.com/tensorflow/tensorflow/commit/d6b57f461b39fd1aa8c1b870f1b974aac3554955).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.
  
### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.
          
### Attribution              
This vulnerability has been reported by Yakun Zhang of Baidu Security.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-wf5p-c75w-w3wh
- https://nvd.nist.gov/vuln/detail/CVE-2021-37689
- https://github.com/tensorflow/tensorflow/commit/d6b57f461b39fd1aa8c1b870f1b974aac3554955
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-602.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-800.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-311.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/149562d49faa709ea80df1d99fc41d005b81082a/tensorflow/compiler/mlir/lite/transforms/optimize.cc#L67-L70
