# [M] browser-use web-ui 2.0.0 through 3.0.0 Cleartext API Key Storage

## Summary
Severity: Medium
Advisory: CVE-2026-82640
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-30
Source: https://osv.dev/vulnerability/CVE-2026-82640
Type: osv

## Details
browser-use web-ui versions 2.0.0 through 3.0.0 write configured LLM API keys to disk in cleartext without encryption or access restrictions. Attackers with read access to the temporary settings directory can recover provider API keys from predictably-named JSON files.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82640.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82640
- https://www.vulncheck.com/advisories/browser-use-web-ui-2.0.0-through-3.0.0-cleartext-api-key-storage
- https://github.com/browser-use/web-ui/issues/736
- https://github.com/browser-use/web-ui
- https://github.com/browser-use/web-ui/blob/v3.0.0/src/webui/webui_manager.py
