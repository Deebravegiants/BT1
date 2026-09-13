# [H] Arbitrary Code Execution via Crafted Keras Config for Model Loading

## Summary
Severity: High
Advisory: GHSA-48g7-3x6r-xfhp
CVE: CVE-2025-1550
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-03-11
Source: https://github.com/advisories/GHSA-48g7-3x6r-xfhp
Type: github-advisory

## Affected
- PyPI: `keras` — affected >=3.0.0 <3.9.0

## Details
### Impact

The Keras `Model.load_model` function permits arbitrary code execution, even with `safe_mode=True`, through a manually constructed, malicious `.keras` archive. By altering the `config.json` file within the archive, an attacker can specify arbitrary Python modules and functions, along with their arguments, to be loaded and executed during model loading.

### Patches

This problem is fixed starting with version `3.9`.

### Workarounds

Only load models from trusted sources and model archives created with Keras.

### References

- https://www.cve.org/cverecord?id=CVE-2025-1550
- https://github.com/keras-team/keras/pull/20751

## References
- https://github.com/keras-team/keras/security/advisories/GHSA-48g7-3x6r-xfhp
- https://nvd.nist.gov/vuln/detail/CVE-2025-1550
- https://github.com/keras-team/keras/pull/20751
- https://github.com/keras-team/keras/commit/e67ac8ffd0c883bec68eb65bb52340c7f9d3a903
- https://github.com/keras-team/keras
- https://github.com/keras-team/keras/releases/tag/v3.9.0
- https://github.com/pypa/advisory-database/tree/main/vulns/keras/PYSEC-2025-122.yaml
- https://towerofhanoi.it/writeups/cve-2025-1550
