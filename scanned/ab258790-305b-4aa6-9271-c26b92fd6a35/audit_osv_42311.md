# [C] Camaleon CMS 2.1.1 - 2.9.1 Authenticated RCE via select_eval Custom Field

## Summary
Severity: Critical
Advisory: CVE-2026-66748
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/CVE-2026-66748
Type: osv

## Details
Camaleon CMS versions 2.1.1 through 2.9.1 contains an authenticated remote code execution vulnerability that allows users with custom_fields manage permission to execute arbitrary Ruby code by supplying a malicious expression through the select_eval custom field type. Attackers can store an attacker-controlled Ruby expression in the field options command parameter, which is evaluated via instance_eval within an ERB view whenever a post edit page is rendered, achieving server-side code execution with web server process privileges.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66748.json
- https://github.com/owen2345/camaleon-cms/releases/tag/2.9.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-66748
- https://www.vulncheck.com/advisories/camaleon-cms-authenticated-rce-via-select-eval-custom-field
- https://github.com/owen2345/camaleon-cms/pull/1136
- https://github.com/owen2345/camaleon-cms/commit/158823668e2e5c3114a69b34cf1c96cb41533c5f
- https://github.com/owen2345/camaleon-cms
- https://enrik-m.github.io/posts/Camaleon-CMS-Vulnerabilties/
- https://github.com/theopaid/Camaleon-CMS---Authenticated-RCE-via-select_eval-Custom-Field
- https://tpaidakis.com/writeups/camaleon-cms-rce-select-eval/
