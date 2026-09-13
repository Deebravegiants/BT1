# [H] fastify-cli vulnerable to remote code execution via ignored explicit Inspector bind address

## Summary
Severity: High
Advisory: CVE-2026-75021
Aliases: GHSA-88v4-3ph7-r88m
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-75021
Type: osv

## Details
fastify-cli starts the Node.js Inspector when a debug flag is used, but it ignores the explicit bind address the user supplies and binds the Inspector to a broadly reachable address instead of the intended loopback. As a result the debugging interface can be exposed beyond the local machine, and because the Inspector protocol allows arbitrary code evaluation, a remote party that reaches it can achieve remote code execution on the developer's machine. This affects fastify-cli from 1.5.0 up to 8.0.1. Users should upgrade to fastify-cli 8.0.1, which honors the configured Inspector bind address.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75021.json
- https://github.com/fastify/fastify-cli/security/advisories/GHSA-88v4-3ph7-r88m
- https://nvd.nist.gov/vuln/detail/CVE-2026-75021
