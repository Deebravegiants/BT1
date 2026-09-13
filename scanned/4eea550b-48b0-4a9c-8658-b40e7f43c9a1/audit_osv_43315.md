# [C] calibre: Bypass of Python template restrictions via nested `template()` leading to RCE

## Summary
Severity: Critical
Advisory: CVE-2026-73248
Aliases: GHSA-4f7g-rjfp-hmvx
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73248
Type: osv

## Details
calibre is an e-book manager. Prior to 9.12.0, calibre processes attacker-controlled composite_template metadata from a malicious EPUB, OPF, PDF, or similar file through program: and a nested template() call whose formatter does not inherit allow_python_templates=False, allowing a nested python: template to reach compile_python_template and execute arbitrary Python code when the file is opened or imported. This issue is fixed in version 9.12.0.

## References
- https://github.com/kovidgoyal/calibre/releases/tag/v9.12.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73248.json
- https://github.com/kovidgoyal/calibre/security/advisories/GHSA-4f7g-rjfp-hmvx
- https://nvd.nist.gov/vuln/detail/CVE-2026-73248
- https://github.com/kovidgoyal/calibre/commit/dac9990458374a81a5372a768bba6527d965aac8
