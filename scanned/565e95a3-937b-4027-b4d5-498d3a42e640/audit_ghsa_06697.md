# [M] Keras: HDF5 virtual datasets can disclose local files

## Summary
Severity: Medium
Advisory: GHSA-26c4-7vv6-867j
CVE: CVE-2026-12480
CWE: CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-26c4-7vv6-867j
Type: github-advisory

## Affected
- PyPI: `keras` — affected >=0 <3.12.3
- PyPI: `keras` — affected >=3.13.0 <3.15.0

## Details
Keras versions up to and including 3.13.2 are vulnerable to an arbitrary HDF5 file read due to an incomplete fix for CVE-2026-1669. The vulnerability resides in the `H5IOStore._verify_dataset()` and `file_editor.py` methods, which fail to check the `dataset.is_virtual` property of HDF5 datasets. This allows an attacker to craft a malicious `.keras` model archive or `.h5` weights file containing a Virtual Dataset (VDS) that references external HDF5 files on the victim's filesystem. When the victim loads the model using `keras.models.load_model()` or `keras.saving.load_model()`, the external file is transparently read, leading to potential information disclosure. Fixed in versions 3.12.3 and 3.15.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-12480
- https://github.com/keras-team/keras/commit/8f987f11bf7512f0df4774a8f1557bba07dc2b49
- https://github.com/keras-team/keras/commit/d5a88bdb137c0d3039b8f4bbbe8c7099925cc10c
- https://github.com/keras-team/keras
- https://github.com/keras-team/keras/releases/tag/v3.12.3
- https://github.com/keras-team/keras/releases/tag/v3.15.0
- https://huntr.com/bounties/1875d257-5b03-4a69-ac70-e98653fa12c7
