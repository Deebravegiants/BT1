# [H] BIT-node-2026-21710

## Summary
Severity: High
Advisory: BIT-node-2026-21710
Aliases: BIT-node-min-2026-21710, CVE-2026-21710
Ecosystem: Bitnami
Published: 2026-04-06
Source: https://osv.dev/vulnerability/BIT-node-2026-21710
Type: osv

## Affected
- Bitnami: `node` — affected >=25.0.0 <25.8.2

## Details
A flaw in Node.js HTTP request handling causes an uncaught `TypeError` when a request is received with a header named `__proto__` and the application accesses `req.headersDistinct`.

When this occurs, `dest["__proto__"]` resolves to `Object.prototype` rather than `undefined`, causing `.push()` to be called on a non-array. This exception is thrown synchronously inside a property getter and cannot be intercepted by `error` event listeners, meaning it cannot be handled without wrapping every `req.headersDistinct` access in a `try/catch`.

* This vulnerability affects all Node.js HTTP servers on **20.x, 22.x, 24.x, and v25.x**

## References
- https://nodejs.org/en/blog/vulnerability/march-2026-security-releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-21710
- https://access.redhat.com/errata/RHSA-2026:7080
- https://access.redhat.com/errata/RHSA-2026:7123
- https://access.redhat.com/errata/RHSA-2026:7302
- https://access.redhat.com/errata/RHSA-2026:7310
- https://access.redhat.com/errata/RHSA-2026:7350
- https://access.redhat.com/errata/RHSA-2026:7670
- https://access.redhat.com/errata/RHSA-2026:7675
- https://access.redhat.com/errata/RHSA-2026:7896
- https://access.redhat.com/errata/RHSA-2026:7983
- https://access.redhat.com/errata/RHSA-2026:8339
- https://access.redhat.com/errata/RHSA-2026:9711
- https://access.redhat.com/errata/RHSA-2026:9874
- https://access.redhat.com/security/cve/CVE-2026-21710
- https://bugzilla.redhat.com/show_bug.cgi?id=2453151
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-21710.json
