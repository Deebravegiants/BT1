# [M] Denial of Service in Tensorflow

## Summary
Severity: Medium
Advisory: GHSA-9mqp-7v2h-2382
CVE: CVE-2020-15194
CWE: CWE-20, CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2020-09-25
Source: https://github.com/advisories/GHSA-9mqp-7v2h-2382
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <1.15.4
- PyPI: `tensorflow` — affected >=2.0.0 <2.0.3
- PyPI: `tensorflow` — affected >=2.1.0 <2.1.2
- PyPI: `tensorflow` — affected >=2.2.0 <2.2.1
- PyPI: `tensorflow` — affected >=2.3.0 <2.3.1
- PyPI: `tensorflow-cpu` — affected >=0 <1.15.4
- PyPI: `tensorflow-cpu` — affected >=2.0.0 <2.0.3
- PyPI: `tensorflow-cpu` — affected >=2.1.0 <2.1.2
- PyPI: `tensorflow-cpu` — affected >=2.2.0 <2.2.1
- PyPI: `tensorflow-cpu` — affected >=2.3.0 <2.3.1
- PyPI: `tensorflow-gpu` — affected >=0 <1.15.4
- PyPI: `tensorflow-gpu` — affected >=2.0.0 <2.0.3
- PyPI: `tensorflow-gpu` — affected >=2.1.0 <2.1.2
- PyPI: `tensorflow-gpu` — affected >=2.2.0 <2.2.1
- PyPI: `tensorflow-gpu` — affected >=2.3.0 <2.3.1

## Details
### Impact
The `SparseFillEmptyRowsGrad` implementation has incomplete validation of the shapes of its arguments:
https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/core/kernels/sparse_fill_empty_rows_op.cc#L235-L241

Although `reverse_index_map_t` and `grad_values_t` are accessed in a similar pattern, only `reverse_index_map_t` is validated to be of proper shape. Hence, malicious users can pass a bad `grad_values_t` to trigger an assertion failure in `vec`, causing denial of service in serving installations.

### Patches
We have patched the issue in 390611e0d45c5793c7066110af37c8514e6a6c54 and will release a patch release for all affected versions.

We recommend users to upgrade to TensorFlow 1.15.4, 2.0.3, 2.1.2, 2.2.1, or 2.3.1.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability is a variant of [GHSA-63xm-rx5p-xvqr](https://github.com/tensorflow/tensorflow/security/advisories/GHSA-63xm-rx5p-xvqr)

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-9mqp-7v2h-2382
- https://nvd.nist.gov/vuln/detail/CVE-2020-15194
- https://github.com/tensorflow/tensorflow/commit/390611e0d45c5793c7066110af37c8514e6a6c54
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-274.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-309.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-117.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.3.1
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00065.html
