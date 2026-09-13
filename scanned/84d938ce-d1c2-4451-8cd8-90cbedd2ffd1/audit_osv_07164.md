# [H] BIT-node-2025-27209

## Summary
Severity: High
Advisory: BIT-node-2025-27209
Aliases: BIT-node-min-2025-27209, CVE-2025-27209
Ecosystem: Bitnami
Published: 2025-07-22
Source: https://osv.dev/vulnerability/BIT-node-2025-27209
Type: osv

## Affected
- Bitnami: `node` — affected >=24.0.0 <24.4.1

## Details
The V8 release used in Node.js v24.0.0 has changed how string hashes are computed using rapidhash. This implementation re-introduces the HashDoS vulnerability as an attacker who can control the strings to be hashed can generate many hash collisions - an attacker can generate collisions even without knowing the hash-seed.

* This vulnerability affects Node.js v24.x users.

## References
- https://nodejs.org/en/blog/vulnerability/july-2025-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2025-27209
- http://www.openwall.com/lists/oss-security/2025/07/22/2
