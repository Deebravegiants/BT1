# [H] BIT-node-2024-21891

## Summary
Severity: High
Advisory: BIT-node-2024-21891
Aliases: BIT-node-min-2024-21891, CVE-2024-21891
Ecosystem: Bitnami
Published: 2024-06-04
Source: https://osv.dev/vulnerability/BIT-node-2024-21891
Type: osv

## Affected
- Bitnami: `node` — affected >=21.0.0 <21.6.2

## Details
Node.js depends on multiple built-in utility functions to normalize paths provided to node:fs functions, which can be overwitten with user-defined implementations leading to filesystem permission model bypass through path traversal attack.
This vulnerability affects all users using the experimental permission model in Node.js 20 and Node.js 21.
Please note that at the time this CVE was issued, the permission model is an experimental feature of Node.js.

## References
- http://www.openwall.com/lists/oss-security/2024/03/11/1
- https://hackerone.com/reports/2259914
- https://security.netapp.com/advisory/ntap-20240315-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2024-21891
- https://github.com/nodejs/node/releases/tag/v20.11.1
- https://github.com/nodejs/node/releases/tag/v21.6.2
- https://nodejs.org/en/blog/vulnerability/february-2024-security-releases#multiple-permission-model-bypasses-due-to-improper-path-traversal-sequence-sanitization-cve-2024-21891---medium
