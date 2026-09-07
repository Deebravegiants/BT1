# [H] Stack overflow in TensorFlow

## Summary
Severity: High
Advisory: GHSA-247x-2f9f-5wp7
CVE: CVE-2022-23591
CWE: CWE-400, CWE-674
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-247x-2f9f-5wp7
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
The `GraphDef` format in TensorFlow does not allow self recursive functions. The runtime assumes that this invariant is satisfied. However, a `GraphDef` containing a fragment such as the following can be consumed when loading a `SavedModel`:

```
  library {
    function {
      signature {
        name: "SomeOp"
        description: "Self recursive op"
      }
      node_def {
        name: "1"
        op: "SomeOp"
      }
      node_def {
        name: "2"
        op: "SomeOp"
      }
    }
  } 
```

This would result in a stack overflow during execution as resolving each `NodeDef` means resolving the function itself and its nodes.

### Patches
We have patched the issue in GitHub commit [448a16182065bd08a202d9057dd8ca541e67996c](https://github.com/tensorflow/tensorflow/commit/448a16182065bd08a202d9057dd8ca541e67996c).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-247x-2f9f-5wp7
- https://nvd.nist.gov/vuln/detail/CVE-2022-23591
- https://github.com/tensorflow/tensorflow/commit/448a16182065bd08a202d9057dd8ca541e67996c
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-100.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-155.yaml
- https://github.com/tensorflow/tensorflow
