# [M] DoS in Calls plugin via malformed msgpack in websocket request.

## Summary
Severity: Medium
Advisory: CVE-2026-2454
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:L)
Published: 2026-03-16
Source: https://osv.dev/vulnerability/CVE-2026-2454
Type: osv

## Details
Mattermost versions 11.3.x <= 11.3.0, 11.2.x <= 11.2.2, 10.11.x <= 10.11.10 fail to handle incorrectly reported array lengths which allows malicious user to cause OOM errors and crash the server via sending corrupted msgpack frames within websocket messages to calls plugin. Mattermost Advisory ID: MMSA-2025-00537

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2454.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-2454
