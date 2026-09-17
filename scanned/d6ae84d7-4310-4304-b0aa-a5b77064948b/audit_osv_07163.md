# [M] BIT-node-2025-23167

## Summary
Severity: Medium
Advisory: BIT-node-2025-23167
Aliases: BIT-node-min-2025-23167, CVE-2025-23167
Ecosystem: Bitnami
Published: 2025-05-21
Source: https://osv.dev/vulnerability/BIT-node-2025-23167
Type: osv

## Affected
- Bitnami: `node` — affected >=0 <20.19.2

## Details
A flaw in Node.js 20's HTTP parser allows improper termination of HTTP/1 headers using `\r\n\rX` instead of the required `\r\n\r\n`.
This inconsistency enables request smuggling, allowing attackers to bypass proxy-based access controls and submit unauthorized requests.

The issue was resolved by upgrading `llhttp` to version 9, which enforces correct header termination.

Impact:
* This vulnerability affects only Node.js 20.x users prior to the `llhttp` v9 upgrade.

## References
- https://nodejs.org/en/blog/vulnerability/may-2025-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2025-23167
