# [H] Loomio 2.22.0 - Code injection

## Summary
Severity: High
Advisory: CVE-2024-1297
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-19
Source: https://osv.dev/vulnerability/CVE-2024-1297
Type: osv

## Details
Loomio version 2.22.0 allows executing arbitrary commands on the server.

This is possible because the application is vulnerable to OS Command Injection.

## References
- https://fluidattacks.com/advisories/stones
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/1xxx/CVE-2024-1297.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-1297
- https://github.com/loomio/loomio/commit/6bc5429bfb5a9c7c811a4487d97ea54a8b23a0fa#diff-b9a7e6b3dfb0fd855c11198a7c53e6f6f90945f28c78cc5dbd960d04d5d28203
- https://github.com/loomio/loomio
