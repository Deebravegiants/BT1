# [M] BIT-node-2026-21712

## Summary
Severity: Medium
Advisory: BIT-node-2026-21712
Aliases: BIT-node-min-2026-21712, CVE-2026-21712
Ecosystem: Bitnami
Published: 2026-04-06
Source: https://osv.dev/vulnerability/BIT-node-2026-21712
Type: osv

## Affected
- Bitnami: `node` — affected >=25.0.0 <25.8.2

## Details
A flaw in Node.js URL processing causes an assertion failure in native code when `url.format()` is called with a malformed internationalized domain name (IDN) containing invalid characters, crashing the Node.js process.

## References
- https://hackerone.com/reports/3546390
- https://nodejs.org/en/blog/vulnerability/march-2026-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-21712
