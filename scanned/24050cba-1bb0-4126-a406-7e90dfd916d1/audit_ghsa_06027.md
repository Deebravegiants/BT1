# [M] Keras: HDF5 links can disclose local file contents

## Summary
Severity: Medium
Advisory: GHSA-m8wh-29wm-52mv
CVE: CVE-2026-9335
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-02
Source: https://github.com/advisories/GHSA-m8wh-29wm-52mv
Type: github-advisory

## Affected
- PyPI: `keras` — affected >=0 <3.12.3
- PyPI: `keras` — affected >=3.13.0 <3.15.0

## Details
A vulnerability in keras-team/keras versions <= 3.14.0 allows arbitrary local HDF5 file content disclosure due to improper handling of HDF5 ExternalLinks. The `KerasFileEditor` and `keras.saving.load_weights` functions bypass the `safe_get_h5_group` and `safe_get_h5_dataset` helpers, which are designed to reject ExternalLinks and SoftLinks. This results in automatic dereferencing of links to external HDF5 files, enabling attackers to disclose sensitive data from the victim's local filesystem. Specifically, `KerasFileEditor` extracts attributes and datasets from linked files into its internal structures, while `keras.saving.load_weights` loads weights from linked files into the user's model. This issue can be exploited by providing a malicious `.h5`, `.weights.h5`, or `.keras` file containing ExternalLinks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9335
- https://github.com/keras-team/keras/pull/22899
- https://github.com/keras-team/keras/pull/23165
- https://github.com/keras-team/keras/commit/23370f16b0ab9a200f7550a34e54a3ceab74ba0e
- https://github.com/keras-team/keras/commit/d338a45204bdc787c8b3c4a9b82c1911cd52dedf
- https://github.com/keras-team/keras
- https://github.com/keras-team/keras/releases/tag/v3.12.3
- https://github.com/keras-team/keras/releases/tag/v3.15.0
- https://huntr.com/bounties/876a7226-5428-4a66-9d05-232461120db5
