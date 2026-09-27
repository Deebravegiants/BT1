# [H] Docling: Unsafe Zip Extraction in EasyOCR Model Download

## Summary
Severity: High
Advisory: GHSA-cjqg-rq2h-2fvj
CVE: CVE-2026-44017
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-cjqg-rq2h-2fvj
Type: github-advisory

## Affected
- PyPI: `docling` — affected >=0 <2.91.0

## Details
### Impact
In versions `< 2.91.0`, The EasyOCR model download functionality extracted ZIP archives without validating member paths, enabling Zip Slip attacks. If an attacker could compromise the model download source (via supply chain attack, DNS spoofing, or MITM), they could write arbitrary files to any location writable by the process, potentially achieving:
- Remote code execution by overwriting Python files or system binaries
- Persistent backdoors by modifying startup scripts or SSH keys
- Data corruption or system compromise

### Patches
Fixed in version 2.91.0. The extraction process now validates each archive member path using `os.path.realpath()` to ensure it remains within the target directory, raising a `SecurityError` for any path traversal attempts.

### Workarounds
Ensure model downloads occur over secure, authenticated channels. Use integrity verification (checksums) for downloaded models. Run the application with minimal file system permissions.

### References
- Fix release: [v2.91.0](https://github.com/docling-project/docling/releases/tag/v2.91.0)

## References
- https://github.com/docling-project/docling/security/advisories/GHSA-cjqg-rq2h-2fvj
- https://nvd.nist.gov/vuln/detail/CVE-2026-44017
- https://access.redhat.com/errata/RHSA-2026:60520
- https://access.redhat.com/security/cve/CVE-2026-44017
- https://bugzilla.redhat.com/show_bug.cgi?id=2492448
- https://github.com/docling-project/docling
- https://github.com/docling-project/docling/releases/tag/v2.91.0
- https://github.com/pypa/advisory-database/tree/main/vulns/docling/PYSEC-2026-2143.yaml
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-44017.json
