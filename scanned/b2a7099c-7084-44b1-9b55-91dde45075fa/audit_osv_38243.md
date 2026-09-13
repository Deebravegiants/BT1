# [H] alf.io has an Authenticated RCE via Extension Script Sandbox Escape

## Summary
Severity: High
Advisory: CVE-2026-35482
Aliases: GHSA-3w8f-mcf6-cm7h
CVSS: 8.0 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-02
Source: https://osv.dev/vulnerability/CVE-2026-35482
Type: osv

## Details
alf.io is an open source ticket reservation system for conferences, trade shows, workshops, and meetups. Prior to version 2.0-M5-2606, a sandbox escape vulnerability in the alf.io extension script engine allows an authenticated administrator to execute arbitrary operating system commands on the server. The extension system is intended to execute restricted JavaScript in a sandboxed Rhino environment; however, a combination of an unguarded injected Java object (`returnClass`) and an incomplete AST blocklist allows the sandbox to be fully escaped using Java reflection without triggering any validation errors. Version 2.0-M5-2606 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35482.json
- https://github.com/alfio-event/alf.io/security/advisories/GHSA-3w8f-mcf6-cm7h
- https://nvd.nist.gov/vuln/detail/CVE-2026-35482
