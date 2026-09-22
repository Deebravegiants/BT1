# [M] WordOps has TOCTOU race condition

## Summary
Severity: Medium
Advisory: GHSA-23qq-p4gq-gc2g
CVE: CVE-2024-34528
CWE: CWE-362, CWE-367
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-05-06
Source: https://github.com/advisories/GHSA-23qq-p4gq-gc2g
Type: github-advisory

## Affected
- PyPI: `wordops` — affected >=0 <3.21.0

## Details
WordOps through 3.20.0 has a `wo/cli/plugins/stack_pref.py` TOCTOU race condition because the `conf_path` `os.open` does not use a mode parameter during file creation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-34528
- https://github.com/WordOps/WordOps/issues/611
- https://github.com/WordOps/WordOps/commit/31353f0fef14ad8bc1f61c028971bd30b9e1909b
- https://github.com/WordOps/WordOps
- https://github.com/WordOps/WordOps/blob/ecf20192c7853925e2cb3f8c8378cd0d86ca0d62/wo/cli/plugins/stack_pref.py#L77
- https://github.com/pypa/advisory-database/tree/main/vulns/wordops/PYSEC-2024-175.yaml
