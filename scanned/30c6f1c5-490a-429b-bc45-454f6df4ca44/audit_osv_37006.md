# [C] SPIP interface_traduction_objets < 2.2.2 Authenticated RCE

## Summary
Severity: Critical
Advisory: CVE-2026-27745
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27745
Type: osv

## Details
The SPIP interface_traduction_objets plugin versions prior to 2.2.2 contain an authenticated remote code execution vulnerability in the translation interface workflow. The plugin incorporates untrusted request data into a hidden form field that is rendered without SPIP output filtering. Because fields prefixed with an underscore bypass protection mechanisms and the hidden content is rendered with filtering disabled, an authenticated attacker with editor-level privileges can inject crafted content that is evaluated through SPIP's template processing chain, resulting in execution of code in the context of the web server.

## References
- https://git.spip.net/spip-contrib-extensions/interface_traduction_objets
- https://plugins.spip.net/interface_traduction_objets
- https://blog.spip.net/Mise-a-jour-de-securite-sortie-de-SPIP-4-4-10.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27745.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-27745
- https://www.vulncheck.com/advisories/spip-interface-traduction-objets-authenticated-rce
- https://git.spip.net/spip-contrib-extensions/interface_traduction_objets/-/commit/db3417b7811774f04c3ff191ca1737fe660ef0be
- https://chocapikk.com/posts/2026/spip-plugins-vulnerabilities/
