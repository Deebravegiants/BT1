# [H] BIT-node-2025-27210

## Summary
Severity: High
Advisory: BIT-node-2025-27210
Aliases: BIT-node-min-2025-27210, CVE-2025-27210
Ecosystem: Bitnami
Published: 2025-07-22
Source: https://osv.dev/vulnerability/BIT-node-2025-27210
Type: osv

## Affected
- Bitnami: `node` — affected >=24.0.0 <24.4.1

## Details
An incomplete fix has been identified for CVE-2025-23084 in Node.js, specifically affecting Windows device names like CON, PRN, and AUX. 

This vulnerability affects Windows users of `path.join` API.

## References
- https://nodejs.org/en/blog/vulnerability/july-2025-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2025-27210
- http://www.openwall.com/lists/oss-security/2025/07/22/2
