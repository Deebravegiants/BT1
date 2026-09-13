# [H] Null-dereference in Tensorflow

## Summary
Severity: High
Advisory: GHSA-8cxv-76p7-jxwr
CVE: CVE-2022-23577
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-8cxv-76p7-jxwr
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
The [implementation of `GetInitOp`](https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/cc/saved_model/loader_util.cc#L31-L61) is vulnerable to a crash caused by dereferencing a null pointer:

```cc
const auto& init_op_sig_it =
    meta_graph_def.signature_def().find(kSavedModelInitOpSignatureKey);
if (init_op_sig_it != sig_def_map.end()) {
  *init_op_name = init_op_sig_it->second.outputs()
                      .find(kSavedModelInitOpSignatureKey)
                      ->second.name();
  return Status::OK();
}
```

Here, we have a nested map and we assume that if the first `.find` succeeds then so would be the search in the internal map. However, the maps are built based on the `SavedModel` protobuf format and a malicious user can alter that on disk before loading to cause the second `.find` to return `nullptr`.
### Patches
We have patched the issue in GitHub commit [4f38b1ac8e42727e18a2f0bde06d3bee8e77b250](https://github.com/tensorflow/tensorflow/commit/4f38b1ac8e42727e18a2f0bde06d3bee8e77b250).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-8cxv-76p7-jxwr
- https://nvd.nist.gov/vuln/detail/CVE-2022-23577
- https://github.com/tensorflow/tensorflow/commit/4f38b1ac8e42727e18a2f0bde06d3bee8e77b250
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-86.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-141.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/cc/saved_model/loader_util.cc#L31-L61
