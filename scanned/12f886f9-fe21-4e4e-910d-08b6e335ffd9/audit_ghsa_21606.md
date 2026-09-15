# [M] Crash due to erroneous `StatusOr` in TensorFlow

## Summary
Severity: Medium
Advisory: GHSA-pqrv-8r2f-7278
CVE: CVE-2022-23590
CWE: CWE-754
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-pqrv-8r2f-7278
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.7.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.7.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.7.1

## Details
### Impact
A `GraphDef` from a TensorFlow `SavedModel` can be maliciously altered to cause a TensorFlow process to crash due to encountering [a `StatusOr` value that is an error and forcibly extracting the value from it](https://github.com/tensorflow/tensorflow/blob/274df9b02330b790aa8de1cee164b70f72b9b244/tensorflow/core/graph/graph.cc#L560-L567):

```cc
  if (op_reg_data->type_ctor != nullptr) {
    VLOG(3) << "AddNode: found type constructor for " << node_def.name();
    const auto ctor_type =
        full_type::SpecializeType(AttrSlice(node_def), op_reg_data->op_def);
    const FullTypeDef ctor_typedef = ctor_type.ValueOrDie();
    if (ctor_typedef.type_id() != TFT_UNSET) {
      *(node_def.mutable_experimental_type()) = ctor_typedef;
    }
  }
```   
      
If `ctor_type` is an error status, `ValueOrDie` results in a crash.
        
### Patches
We have patched the issue in GitHub commit [955059813cc325dc1db5e2daa6221271406d4439](https://github.com/tensorflow/tensorflow/commit/955059813cc325dc1db5e2daa6221271406d4439).
  
We have patched the issue in multiple GitHub commits and these will be included in TensorFlow 2.8.0 and TensorFlow 2.7.1, as both are affected.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-pqrv-8r2f-7278
- https://nvd.nist.gov/vuln/detail/CVE-2022-23590
- https://github.com/tensorflow/tensorflow/commit/955059813cc325dc1db5e2daa6221271406d4439
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-99.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-154.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/274df9b02330b790aa8de1cee164b70f72b9b244/tensorflow/core/graph/graph.cc#L560-L567
