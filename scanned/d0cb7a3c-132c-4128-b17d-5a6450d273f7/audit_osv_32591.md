# [C] Conda-build vulnerable to supply chain attack vector due to pyproject.toml referring to dependencies not present in PyPI

## Summary
Severity: Critical
Advisory: CVE-2025-32800
Aliases: GHSA-83gh-p93g-cwgx
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2025-06-16
Source: https://osv.dev/vulnerability/CVE-2025-32800
Type: osv

## Details
Conda-build contains commands and tools to build conda packages. Prior to version 25.3.0, the pyproject.toml lists conda-index as a Python dependency. This package is not published in PyPI. An attacker could claim this namespace and upload arbitrary (malicious) code to the package, and then exploit pip install commands by injecting the malicious dependency in the solve. This issue has been fixed in version 25.3.0. A workaround involves using --no-deps for pip install-ing the project from the repository.

## References
- https://drive.google.com/file/d/18qe97zxcpTn2l84187A9meGCi2Wg-n_Y/view
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32800.json
- https://github.com/conda/conda-build/security/advisories/GHSA-83gh-p93g-cwgx
- https://nvd.nist.gov/vuln/detail/CVE-2025-32800
- https://github.com/conda/conda-build/commit/f5a6aeef0d5d6940b8c2a88796910dc7476a62bb
