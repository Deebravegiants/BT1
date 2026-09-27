# [M] TensorFlow vulnerable to null-dereference in `mlir::tfg::TFOp::nameAttr`

## Summary
Severity: Medium
Advisory: GHSA-7j3m-8g3c-9qqq
CVE: CVE-2022-36014
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-7j3m-8g3c-9qqq
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
When [`mlir::tfg::TFOp::nameAttr`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/ir/importexport/graphdef_import.cc) receives null type list attributes, it crashes.
```cpp

StatusOr<unsigned> GraphDefImporter::ArgNumType(const NamedAttrList &attrs,
                                                const OpDef::ArgDef &arg_def,
                                                SmallVectorImpl<Type> &types) {
  // Check whether a type list attribute is specified.
  if (!arg_def.type_list_attr().empty()) {
    if (auto v = attrs.get(arg_def.type_list_attr()).dyn_cast<ArrayAttr>()) {
      for (Attribute attr : v) {
        if (auto dtype = attr.dyn_cast<TypeAttr>()) {
          types.push_back(UnrankedTensorType::get(dtype.getValue()));
        } else {
          return InvalidArgument("Expected '", arg_def.type_list_attr(),
                                 "' to be a list of types");
        }
      }
      return v.size();
    }
    return NotFound("Type attr not found: ", arg_def.type_list_attr());
  }

  unsigned num = 1;
  // Check whether a number attribute is specified.
  if (!arg_def.number_attr().empty()) {
    if (auto v = attrs.get(arg_def.number_attr()).dyn_cast<IntegerAttr>()) {
      num = v.getValue().getZExtValue();
    } else {
      return NotFound("Type attr not found: ", arg_def.number_attr());
    }
  }

  // Check for a type or type attribute.
  Type dtype;
  if (arg_def.type() != DataType::DT_INVALID) {
    TF_RETURN_IF_ERROR(ConvertDataType(arg_def.type(), b_, &dtype));
  } else if (arg_def.type_attr().empty()) {
    return InvalidArgument("Arg '", arg_def.name(),
                           "' has invalid type and no type attribute");
  } else {
    if (auto v = attrs.get(arg_def.type_attr()).dyn_cast<TypeAttr>()) {
      dtype = v.getValue();
    } else {
      return NotFound("Type attr not found: ", arg_def.type_attr());
    }
  }
  types.append(num, UnrankedTensorType::get(dtype));
  return num;
}
```


### Patches
We have patched the issue in GitHub commits [3a754740d5414e362512ee981eefba41561a63a6](https://github.com/tensorflow/tensorflow/commit/3a754740d5414e362512ee981eefba41561a63a6) and [a0f0b9a21c9270930457095092f558fbad4c03e5](https://github.com/tensorflow/tensorflow/commit/a0f0b9a21c9270930457095092f558fbad4c03e5).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-7j3m-8g3c-9qqq
- https://nvd.nist.gov/vuln/detail/CVE-2022-36014
- https://github.com/tensorflow/tensorflow/commit/3a754740d5414e362512ee981eefba41561a63a6
- https://github.com/tensorflow/tensorflow/commit/a0f0b9a21c9270930457095092f558fbad4c03e5
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/ir/importexport/graphdef_import.cc
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
