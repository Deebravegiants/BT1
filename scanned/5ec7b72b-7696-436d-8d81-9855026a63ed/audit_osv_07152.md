# [H] BIT-node-2024-22017

## Summary
Severity: High
Advisory: BIT-node-2024-22017
Aliases: BIT-node-min-2024-22017, CVE-2024-22017
Ecosystem: Bitnami
Published: 2024-11-29
Source: https://osv.dev/vulnerability/BIT-node-2024-22017
Type: osv

## Affected
- Bitnami: `node` — affected >=21.0.0 <21.6.2

## Details
setuid() does not affect libuv's internal io_uring operations if initialized before the call to setuid().
This allows the process to perform privileged operations despite presumably having dropped such privileges through a call to setuid().
This vulnerability affects all users using version greater or equal than Node.js 18.18.0, Node.js 20.4.0 and Node.js 21.

## References
- http://www.openwall.com/lists/oss-security/2024/03/11/1
- https://hackerone.com/reports/2170226
- https://security.netapp.com/advisory/ntap-20240517-0007/
- https://nvd.nist.gov/vuln/detail/CVE-2024-22017
- https://github.com/nodejs/node/releases/tag/v20.11.1
- https://github.com/nodejs/node/releases/tag/v21.6.2
- https://nodejs.org/en/blog/vulnerability/february-2024-security-releases#setuid-does-not-drop-all-privileges-due-to-io_uring-cve-2024-22017---high
