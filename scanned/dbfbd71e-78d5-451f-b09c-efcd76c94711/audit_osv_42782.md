# [H] Zigbee2MQTT External JS Extension Path Traversal Leading to Remote Code Execution

## Summary
Severity: High
Advisory: CVE-2026-71279
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71279
Type: osv

## Details
Zigbee2MQTT's ExternalJSExtension.getFilePath (lib/extension/externalJS.ts) joins a parameter received via an MQTT message (topic zigbee2mqtt/bridge/request/extension/save) into the extensions base path using path.join(basePath, name) with no sanitization. The extension handler only validates that the name ends in .js/.mjs/.cjs, writes the file, and then dynamically imports it via Node.js import, achieving remote code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71279.json
- https://github.com/Koenkk/zigbee2mqtt
- https://github.com/Koenkk/zigbee2mqtt/blob/master/lib/extension/externalJS.ts
- https://nvd.nist.gov/vuln/detail/CVE-2026-71279
