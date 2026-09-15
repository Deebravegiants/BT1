# [C] Microsoft UFO: Unauthenticated Mobile MCP access allows remote Android device control and screen disclosure

## Summary
Severity: Critical
Advisory: CVE-2026-73296
Aliases: GHSA-24fq-m9rr-g3mm
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73296
Type: osv

## Details
Microsoft UFO open-source framework for intelligent automation across devices and platforms. Prior to 3.0.8, create_mobile_data_collection_server and create_mobile_action_server in ufo/client/mcp/http_servers/mobile_mcp_server.py exposed Streamable HTTP MCP services on TCP ports 8020 and 8021 without authentication, allowing an unauthenticated remote attacker to invoke capture_screenshot, get_ui_tree, tap, swipe, type_text, launch_app, press_key, and click_control against an ADB-connected Android device, disclose screen and device data, and modify device state. This issue is fixed in version 3.0.8.

## References
- https://github.com/microsoft/UFO/releases/tag/v3.0.8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73296.json
- https://github.com/microsoft/UFO/security/advisories/GHSA-24fq-m9rr-g3mm
- https://nvd.nist.gov/vuln/detail/CVE-2026-73296
- https://github.com/microsoft/UFO/commit/e562d10060b077dedae93e0fd58c1ee379558962
