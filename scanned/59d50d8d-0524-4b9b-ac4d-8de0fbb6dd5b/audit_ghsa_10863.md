# [C] Convict has prototype pollution via load(), loadFile(), and schema initialization

## Summary
Severity: Critical
Advisory: GHSA-hf2r-9gf9-rwch
CVE: CVE-2026-33863
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-hf2r-9gf9-rwch
Type: github-advisory

## Affected
- npm: `convict` — affected >=0 <6.2.5

## Details
### Impact
Two unguarded prototype pollution paths exist, not covered by previous fixes:

1. `config.load()` / `config.loadFile()` — `overlay()` recursively merges config data without checking for forbidden keys. Input containing` __proto__` or `constructor.prototype` (e.g. from a JSON file) causes the recursion to reach `Object.prototype` and write attacker-controlled values onto it.
2. Schema initialization — passing a schema with `constructor.prototype.*` keys to `convict({...})` causes default-value propagation to write directly to `Object.prototype` at startup.

Depending on how polluted properties are consumed, impact ranges from unexpected behavior to authentication bypass or RCE.

### Workarounds
Do not pass untrusted data to load(), loadFile(), or convict().

### Resources
Prior advisory: [GHSA-44fc-8fm5-q62h](https://github.com/mozilla/node-convict/security/advisories/GHSA-44fc-8fm5-q62h)
Related issue: [https://github.com/mozilla/node-convict/issues/423](https://github.com/mozilla/node-convict/issues/423)

## References
- https://github.com/mozilla/node-convict/security/advisories/GHSA-44fc-8fm5-q62h
- https://github.com/mozilla/node-convict/security/advisories/GHSA-hf2r-9gf9-rwch
- https://github.com/mozilla/node-convict/issues/423
- https://github.com/mozilla/node-convict
