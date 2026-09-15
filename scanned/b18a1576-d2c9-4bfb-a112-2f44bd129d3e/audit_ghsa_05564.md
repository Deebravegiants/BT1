# [H] docling-core vulnerable to Remote Code Execution via unsafe PyYAML usage

## Summary
Severity: High
Advisory: GHSA-vqxf-v2gg-x3hc
CVE: CVE-2026-24009
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-22
Source: https://github.com/advisories/GHSA-vqxf-v2gg-x3hc
Type: github-advisory

## Affected
- PyPI: `docling-core` — affected >=2.21.0 <2.48.4

## Details
### Impact

A PyYAML-related Remote Code Execution (RCE) vulnerability, namely CVE-2020-14343, is exposed in `docling-core >=2.21.0, <2.48.4` and, specifically only if the application uses `pyyaml < 5.4` and invokes `docling_core.types.doc.DoclingDocument.load_from_yaml()` passing it untrusted YAML data.

### Patches

The vulnerability has been patched in `docling-core` version **2.48.4**.
The fix mitigates the issue by switching `PyYAML` deserialization from `yaml.FullLoader` to `yaml.SafeLoader`, ensuring that untrusted data cannot trigger code execution.

### Workarounds

Users who cannot immediately upgrade `docling-core` can alternatively ensure that the installed version of `PyYAML` is **5.4 or greater**, which supposedly patches CVE-2020-14343.

### References

* GitHub Issue: #482
* Upstream Advisory: CVE-2020-14343
* Fix Release: [v2.48.4](https://github.com/docling-project/docling-core/releases/tag/v2.48.4)

## References
- https://github.com/docling-project/docling-core/security/advisories/GHSA-vqxf-v2gg-x3hc
- https://nvd.nist.gov/vuln/detail/CVE-2026-24009
- https://github.com/docling-project/docling-core/issues/482
- https://github.com/docling-project/docling-core/commit/3e8d628eeeae50f0f8f239c8c7fea773d065d80c
- https://github.com/advisories/GHSA-8q59-q68h-6hv4
- https://github.com/docling-project/docling-core
- https://github.com/docling-project/docling-core/releases/tag/v2.48.4
