# [H] CVE-2024-34997

## Summary
Severity: High
Advisory: CVE-2024-34997
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-34997
Type: osv

## Details
joblib v1.4.2 was discovered to contain a deserialization vulnerability via the component joblib.numpy_pickle::NumpyArrayWrapper().read_array(). NOTE: this is disputed by the supplier because NumpyArrayWrapper is only used during caching of trusted content.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34997.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34997
- https://github.com/joblib/joblib/issues/1582
- https://github.com/joblib/joblib/issues/977
