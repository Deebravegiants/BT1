# [M] TensorFlow vulnerable to null-dereference in `mlir::tfg::GraphDefImporter::ConvertNodeDef`

## Summary
Severity: Medium
Advisory: GHSA-828c-5j5q-vrjq
CVE: CVE-2022-36013
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-828c-5j5q-vrjq
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.7.2
- PyPI: `tensorflow` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.7.2
- PyPI: `tensorflow-cpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-cpu` — affected >=2.9.0 <2.9.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.7.2
- PyPI: `tensorflow-gpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-gpu` — affected >=2.9.0 <2.9.1

## Details
### Impact
When [`mlir::tfg::GraphDefImporter::ConvertNodeDef`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/ir/importexport/graphdef_import.cc) tries to convert NodeDefs without an op name, it crashes.
```cpp
Status GraphDefImporter::ConvertNodeDef(OpBuilder &builder, ConversionState &s,
                                        const NodeDef &node) {
  VLOG(4) << "Importing: " << node.name();
  OperationState state(ConvertLocation(node), absl::StrCat("tfg.", node.op()));

  // The GraphImporter does light shape inference, but here we will defer all of
  // that to the shape inference pass.
  const OpDef *op_def;
  const OpRegistrationData *op_reg_data = nullptr;
  if ((op_reg_data = registry_.LookUp(node.op()))) {
    op_def = &op_reg_data->op_def;
  } else {
    auto it = function_op_defs_.find(node.op());
    if (it == function_op_defs_.end())
      return InvalidArgument("Unable to find OpDef for ", node.op());
    op_def = it->second;
  }
```
`node.op().empty()` cannot be empty.


### Patches
We have patched the issue in GitHub commit [a0f0b9a21c9270930457095092f558fbad4c03e5](https://github.com/tensorflow/tensorflow/commit/a0f0b9a21c9270930457095092f558fbad4c03e5).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-828c-5j5q-vrjq
- https://nvd.nist.gov/vuln/detail/CVE-2022-36013
- https://github.com/tensorflow/tensorflow/commit/a0f0b9a21c9270930457095092f558fbad4c03e5
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/ir/importexport/graphdef_import.cc
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
