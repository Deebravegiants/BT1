# [M] Segfault on strings tensors with mistmatched dimensions, due to Go code

## Summary
Severity: Medium
Advisory: GHSA-cmgw-8vpc-rc59
CVE: CVE-2021-37692
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-cmgw-8vpc-rc59
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.5.0rc0 <2.5.1
- PyPI: `tensorflow-cpu` — affected >=2.5.0rc0 <2.5.1
- PyPI: `tensorflow-gpu` — affected >=2.5.0rc0 <2.5.1

## Details
### Impact
Under certain conditions, Go code can trigger a segfault in string deallocation.


For string tensors, `C.TF_TString_Dealloc` is called during garbage collection within a finalizer function.  However, tensor structure isn't checked until encoding to avoid a performance penalty.  The current method for dealloc assumes that encoding succeeded, but segfaults when a string tensor is garbage collected whose encoding failed (e.g., due to mismatched dimensions).

To fix this, the call to set the finalizer function is deferred until `NewTensor` returns and, if encoding failed for a string tensor, deallocs are determined based on bytes written.

### Patches
We have patched the issue in GitHub commit [8721ba96e5760c229217b594f6d2ba332beedf22](https://github.com/tensorflow/tensorflow/commit/8721ba96e5760c229217b594f6d2ba332beedf22) (merging [#50508](https://github.com/tensorflow/tensorflow/pull/50508)).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, which is the other affected version.                                                                                                                                               

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported externally via a [fixing PR](https://github.com/tensorflow/tensorflow/pull/50508).

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-cmgw-8vpc-rc59
- https://nvd.nist.gov/vuln/detail/CVE-2021-37692
- https://github.com/tensorflow/tensorflow/pull/50508
- https://github.com/tensorflow/tensorflow/commit/8721ba96e5760c229217b594f6d2ba332beedf22
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-605.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-803.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-314.yaml
- https://github.com/tensorflow/tensorflow
