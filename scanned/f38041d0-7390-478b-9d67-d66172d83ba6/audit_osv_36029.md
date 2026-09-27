# [M] HDF5 H5Pget_fill_value NULL Pointer Dereference via Malformed Fill Value Message

## Summary
Severity: Medium
Advisory: CVE-2026-19024
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-19024
Type: osv

## Details
NULL pointer dereference in H5Pget_fill_value in HDF5 before 2.3.0 allows attackers to cause a denial of service via a dataset whose version 1 or 2 fill value message has the "defined" flag set together with a negative size field, which is not normalized to the library's "undefined" sentinel and reaches H5T_path_find with a NULL datatype.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19024.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19024
- https://github.com/HDFGroup/hdf5/issues/6487
