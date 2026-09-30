# [M] Blueprint Studio terminal SSH private key written to disk

## Summary
Severity: Medium
Advisory: CVE-2026-53456
Aliases: GHSA-3vg8-xf27-7q45
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-53456
Type: osv

## Details
Blueprint Studio is a VS Code-like file editor for Home Assistant configuration files. Prior to 2.5.2, Blueprint Studio terminal SSH key authentication in custom_components/blueprint_studio/backend/terminal_manager.py wrote SSH private-key material to a file under the Home Assistant configuration directory before applying restrictive permissions and relied on best-effort cleanup. The key could temporarily remain on disk and could persist if cleanup failed or Home Assistant crashed. A user or process with filesystem access to the Home Assistant configuration directory could obtain the residual private key. This issue is fixed in version 2.5.2.

## References
- https://github.com/ha-china/blueprint-studio/releases/tag/v2.5.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53456.json
- https://github.com/ha-china/blueprint-studio/security/advisories/GHSA-3vg8-xf27-7q45
- https://nvd.nist.gov/vuln/detail/CVE-2026-53456
- https://github.com/ha-china/blueprint-studio/commit/943aed0be67f3a910b0f70a3864288d5e17e55ce
