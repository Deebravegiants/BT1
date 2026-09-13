# [M] Memory leak in Tensorflow

## Summary
Severity: Medium
Advisory: GHSA-8r7c-3cm2-3h8f
CVE: CVE-2022-23578
CWE: CWE-401
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-8r7c-3cm2-3h8f
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
If a graph node is invalid, TensorFlow can leak memory in the [implementation of `ImmutableExecutorState::Initialize`](https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/common_runtime/immutable_executor_state.cc#L84-L262):

```cc
Status s = params_.create_kernel(n->properties(), &item->kernel);
if (!s.ok()) {
  item->kernel = nullptr;
  s = AttachDef(s, *n);
  return s;           
}                     
```

Here, we set `item->kernel` to `nullptr` but it is a simple `OpKernel*` pointer so the memory that was previously allocated to it would leak.

### Patches
We have patched the issue in GitHub commit [c79ccba517dbb1a0ccb9b01ee3bd2a63748b60dd](https://github.com/tensorflow/tensorflow/commit/c79ccba517dbb1a0ccb9b01ee3bd2a63748b60dd).
The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information 
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-8r7c-3cm2-3h8f
- https://nvd.nist.gov/vuln/detail/CVE-2022-23578
- https://github.com/tensorflow/tensorflow/commit/c79ccba517dbb1a0ccb9b01ee3bd2a63748b60dd
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-87.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-142.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/common_runtime/immutable_executor_state.cc#L84-L262
