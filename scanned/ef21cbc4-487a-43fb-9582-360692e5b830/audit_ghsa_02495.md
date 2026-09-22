# [M] Infinite loop in TFLite

## Summary
Severity: Medium
Advisory: GHSA-mhhc-q96p-mfm9
CVE: CVE-2021-37686
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-mhhc-q96p-mfm9
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.6.0rc0 <2.6.0rc2
- PyPI: `tensorflow-cpu` — affected >=2.6.0rc0 <2.6.0rc2
- PyPI: `tensorflow-gpu` — affected >=2.6.0rc0 <2.6.0rc2

## Details
### Impact
The strided slice implementation in TFLite has a logic bug which can allow an attacker to trigger an infinite loop. This arises from newly introduced support for [ellipsis in axis definition](https://github.com/tensorflow/tensorflow/blob/149562d49faa709ea80df1d99fc41d005b81082a/tensorflow/lite/kernels/strided_slice.cc#L103-L122):

```cc
  for (int i = 0; i < effective_dims;) {
    if ((1 << i) & op_context->params->ellipsis_mask) {
      // ...
      int ellipsis_end_idx =
          std::min(i + 1 + num_add_axis + op_context->input_dims - begin_count,
                   effective_dims);
      // ...
      for (; i < ellipsis_end_idx; ++i) {
        // ...
      }
      continue;
    }
    // ...
    ++i;
  }
```

An attacker can craft a model such that `ellipsis_end_idx` is smaller than `i` (e.g., always negative). In this case, the inner loop does not increase `i` and the `continue` statement causes execution to skip over the preincrement at the end of the outer loop.

### Patches
We have patched the issue in GitHub commit [dfa22b348b70bb89d6d6ec0ff53973bacb4f4695](https://github.com/tensorflow/tensorflow/commit/dfa22b348b70bb89d6d6ec0ff53973bacb4f4695).

The fix will be included in TensorFlow 2.6.0. This is the only affected version.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-mhhc-q96p-mfm9
- https://nvd.nist.gov/vuln/detail/CVE-2021-37686
- https://github.com/tensorflow/tensorflow/commit/dfa22b348b70bb89d6d6ec0ff53973bacb4f4695
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-599.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-797.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-308.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.3.4
- https://github.com/tensorflow/tensorflow/releases/tag/v2.4.3
- https://github.com/tensorflow/tensorflow/releases/tag/v2.5.1
- https://github.com/tensorflow/tensorflow/releases/tag/v2.6.0
