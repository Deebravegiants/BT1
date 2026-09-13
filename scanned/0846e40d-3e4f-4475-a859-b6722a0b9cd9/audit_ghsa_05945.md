# [M] Keras model loading is vulnerable to denial of service through HDF5 shape bombs

## Summary
Severity: Medium
Advisory: GHSA-74m6-m3xx-3vmj
CVE: CVE-2026-12570
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-10
Source: https://github.com/advisories/GHSA-74m6-m3xx-3vmj
Type: github-advisory

## Affected
- PyPI: `keras` — affected >=0 <3.15.0

## Details
A vulnerability in keras-team/keras versions < 3.15.0 allows for a denial of service (DoS) attack when loading malicious .keras model files via the keras.models.load_model() function. The H5IOStore.__getitem__ method in keras/src/saving/saving_lib.py does not validate the shape or size of datasets, leading to unbounded memory allocation. A specially crafted .keras file can exploit this flaw to trigger an out-of-memory (OOM) condition, causing the process to be terminated (exit code 137). This issue bypasses the fix for CVE-2026-0897, which only addressed a similar vulnerability in KerasFileEditor. The attack vector includes poisoned models from public repositories or malicious model registries, posing a risk to machine learning pipelines that process untrusted models.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-12570
- https://github.com/keras-team/keras/pull/22975
- https://github.com/keras-team/keras/commit/4933ea4a5b3fcc24ceacdc276f5bb5dfbd06756c
- https://github.com/keras-team/keras
- https://github.com/keras-team/keras/releases/tag/v3.15.0
- https://huntr.com/bounties/a064f475-780a-409a-82f7-678512f27ad8
