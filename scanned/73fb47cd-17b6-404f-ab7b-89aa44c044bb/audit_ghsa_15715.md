# [H] TensorFlow has segfault in array_ops.upper_bound

## Summary
Severity: High
Advisory: GHSA-gjh7-xx4r-x345
CVE: CVE-2023-33976
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-30
Source: https://github.com/advisories/GHSA-gjh7-xx4r-x345
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.12.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.12.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.12.1

## Details
### Impact
`array_ops.upper_bound` causes a segfault when not given a rank 2 tensor.

### Patches
We have patched the issue in GitHub commit [915884fdf5df34aaedd00fc6ace33a2cfdefa586](https://github.com/tensorflow/tensorflow/commit/915884fdf5df34aaedd00fc6ace33a2cfdefa586).

The fix will be included in TensorFlow 2.13. We will also cherrypick this commit in TensorFlow 2.12.1.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by dmc1778

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-gjh7-xx4r-x345
- https://nvd.nist.gov/vuln/detail/CVE-2023-33976
- https://github.com/tensorflow/tensorflow/commit/6fa05df43b00038b048f4f0e51ef522da6532fec
- https://github.com/tensorflow/tensorflow/commit/915884fdf5df34aaedd00fc6ace33a2cfdefa586
- https://github.com/tensorflow/tensorflow
