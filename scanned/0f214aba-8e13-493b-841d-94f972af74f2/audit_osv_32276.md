# [M] Path Traversal Vulnerability in GHOSTS Photo Retrieval Endpoint

## Summary
Severity: Medium
Advisory: CVE-2025-27092
Aliases: GHSA-qr67-m6w9-wj3j
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2025-02-19
Source: https://osv.dev/vulnerability/CVE-2025-27092
Type: osv

## Details
GHOSTS is an open source user simulation framework for cyber experimentation, simulation, training, and exercise. A path traversal vulnerability was discovered in GHOSTS version 8.0.0.0 that allows an attacker to access files outside of the intended directory through the photo retrieval endpoint. The vulnerability exists in the /api/npcs/{id}/photo endpoint, which is designed to serve profile photos for NPCs (Non-Player Characters) but fails to properly validate and sanitize file paths. When an NPC is created with a specially crafted photoLink value containing path traversal sequences (../, ..\, etc.), the application processes these sequences without proper sanitization. This allows an attacker to traverse directory structures and access files outside of the intended photo directory, potentially exposing sensitive system files. The vulnerability is particularly severe because it allows reading arbitrary files from the server's filesystem with the permissions of the web application process, which could include configuration files, credentials, or other sensitive data. This issue has been addressed in version 8.2.7.90 and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27092.json
- https://github.com/cmu-sei/GHOSTS/security/advisories/GHSA-qr67-m6w9-wj3j
- https://nvd.nist.gov/vuln/detail/CVE-2025-27092
- https://github.com/cmu-sei/GHOSTS/commit/e69827556a52ff813de00e1017c4b62598d2c887
