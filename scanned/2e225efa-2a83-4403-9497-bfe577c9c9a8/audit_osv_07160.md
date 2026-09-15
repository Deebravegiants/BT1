# [M] BIT-node-2025-23084

## Summary
Severity: Medium
Advisory: BIT-node-2025-23084
Aliases: BIT-node-min-2025-23084, CVE-2025-23084
Ecosystem: Bitnami
Published: 2025-01-30
Source: https://osv.dev/vulnerability/BIT-node-2025-23084
Type: osv

## Affected
- Bitnami: `node` — affected >=23.0.0 <23.8.0

## Details
A vulnerability has been identified in Node.js, specifically affecting the handling of drive names in the Windows environment. Certain Node.js functions do not treat drive names as special on Windows. As a result, although Node.js assumes a relative path, it actually refers to the root directory.

On Windows, a path that does not start with the file separator is treated as relative to the current directory. 

This vulnerability affects Windows users of `path.join` API.

## References
- https://nodejs.org/en/blog/vulnerability/january-2025-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2025-23084
- http://www.openwall.com/lists/oss-security/2025/07/22/2
- https://security.netapp.com/advisory/ntap-20250321-0003/
