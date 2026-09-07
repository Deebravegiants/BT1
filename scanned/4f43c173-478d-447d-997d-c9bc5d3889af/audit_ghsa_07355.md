# [H] find-my-way: DDoS with HTTP2

## Summary
Severity: High
Advisory: GHSA-c96f-x56v-gq3h
CVE: CVE-2026-47219
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-23
Source: https://github.com/advisories/GHSA-c96f-x56v-gq3h
Type: github-advisory

## Affected
- npm: `find-my-way` — affected >=0 <9.7.0

## Details
### Impact
Remotely triggerable DoS in find-my-way when it is used with Node's HTTP/2 server.

The short version is that `lookup()` passes `req.method` into `find()`, and `find()` indexes `this.trees[method]`. Since `this.trees` is a normal object, HTTP/2 method values like constructor, `toString`, or `__proto__` can resolve inherited object properties instead of returning undefined. The code then treats that value like a router node and crashes when it reaches `currentNode.prefix.length`.

### Patches

Upgrade to v9.7.0.

### Workarounds

Do not use find-my-way with HTTP/2 servers, or validate that the http method is valid beforehand.

## References
- https://github.com/delvedor/find-my-way/security/advisories/GHSA-c96f-x56v-gq3h
- https://github.com/delvedor/find-my-way/pull/434
- https://github.com/delvedor/find-my-way/commit/cfe3fd6168b5ac1594c0820fb83fce251a533fc1
- https://github.com/delvedor/find-my-way
- https://github.com/delvedor/find-my-way/releases/tag/v9.7.0
