# [M] OpenHarness Permission Bypass via grep and glob root argument

## Summary
Severity: Medium
Advisory: CVE-2026-40515
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/CVE-2026-40515
Type: osv

## Details
OpenHarness before commit bd4df81 contains a permission bypass vulnerability that allows attackers to read sensitive files by exploiting incomplete path normalization in the permission checker. Attackers can invoke the built-in grep and glob tools with sensitive root directories that are not properly evaluated against configured path rules, allowing disclosure of sensitive local file content, key material, configuration files, or directory contents despite configured path restrictions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40515.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40515
- https://www.vulncheck.com/advisories/openharness-permission-bypass-via-grep-and-glob-root-argument
- https://github.com/HKUDS/OpenHarness/pull/92
- https://github.com/HKUDS/OpenHarness/commit/bd4df81f634f8c7cddcc3fdf7f561a13dcbf03ae
- https://github.com/HKUDS/OpenHarness
