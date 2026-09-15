# [C] MikroORM is vulnerable to SQL Injection via specially crafted object

## Summary
Severity: Critical
Advisory: GHSA-gwhv-j974-6fxm
CVE: CVE-2026-34220
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-gwhv-j974-6fxm
Type: github-advisory

## Affected
- npm: `@mikro-orm/core` — affected >=0 <6.6.10
- npm: `@mikro-orm/core` — affected >=7.0.0-dev.0 <7.0.6

## Details
## Summary

MikroORM versions <= 6.6.9 and <= 7.0.5 are vulnerable to SQL injection when specially crafted objects are interpreted as raw SQL query fragments.

## Impact

If user-controlled input is passed directly to MikroORM query construction APIs, an attacker may inject raw SQL fragments. This can lead to SQL injection depending on the database and query being executed.

## Affected usage

The issue occurs when untrusted objects are passed to ORM write APIs such as:

- `wrap(entity).assign(userInput)` followed by `em.flush()`
- `em.nativeUpdate()`
- `em.nativeInsert()`
- `em.create()` followed by `em.flush()`

Applications that validate input types or enforce strict schema validation before passing data to MikroORM are not affected.

## Fix

The vulnerability was caused by duck-typed detection of internal ORM marker properties.

The fix replaces these checks with symbol-based markers that cannot be reproduced by user input.

## References
- https://github.com/mikro-orm/mikro-orm/security/advisories/GHSA-gwhv-j974-6fxm
- https://nvd.nist.gov/vuln/detail/CVE-2026-34220
- https://github.com/mikro-orm/mikro-orm
