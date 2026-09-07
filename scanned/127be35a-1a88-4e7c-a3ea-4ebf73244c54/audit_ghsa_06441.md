# [H] fast-uri vulnerable to host confusion via percent-encoded scheme normalization

## Summary
Severity: High
Advisory: GHSA-jqff-g426-hqxp
CVE: CVE-2026-76172
CWE: CWE-177
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-jqff-g426-hqxp
Type: github-advisory

## Affected
- npm: `fast-uri` — affected >=2.3.1 <2.4.5
- npm: `fast-uri` — affected >=3.0.0 <3.1.6
- npm: `fast-uri` — affected >=4.0.0 <4.1.3

## Details
### Impact

`fast-uri` decodes percent-encoded characters in the scheme component with the legacy global `unescape()` and serializes the result back as raw characters, without re-escaping it or validating it as a scheme. A scheme that decodes to characters outside the RFC 3986 scheme grammar can therefore introduce structure the original input did not contain.

For example, `%2f%2fevil.example:/pwn` parses with no authority (`parse().host` is `undefined`), but `resolve()` and `normalize()` return `//evil.example:/pwn`, which reparses with host `evil.example`. The `%uXXXX` form (`%u002f%u002fevil.example:/pwn`) produces the same result, and a scheme containing `%0d%0a` reaches the output as a raw CR LF.

Applications that normalize or resolve untrusted URLs before a redirect check, host allowlist, or outbound request decision, especially ones that treat a missing authority as same-origin, can be steered to an attacker-chosen authority, and a normalized URI placed in a response header can carry an injected CR LF.

### Patches

Upgrade to `fast-uri` >= 4.1.3, or >= 3.1.6 in the v3.x release line, or >= 2.4.5 in the v2.x release line.

### Workarounds

None. Upgrade to the patched version.

## References
- https://github.com/fastify/fast-uri/security/advisories/GHSA-jqff-g426-hqxp
- https://nvd.nist.gov/vuln/detail/CVE-2026-76172
- https://github.com/fastify/fast-uri/commit/37f3417c82994279656854f83ce938acd81c3862
- https://github.com/fastify/fast-uri/commit/a941e626411f576f8d90883231e57b6c9d0ff98b
- https://github.com/fastify/fast-uri/commit/c6a74bfd9d8c6b0df5362b3c7ae88d8021cb1e39
- https://cna.openjsf.org/security-advisories.html
- https://github.com/fastify/fast-uri
- https://github.com/fastify/fast-uri/releases/tag/v2.4.5
- https://github.com/fastify/fast-uri/releases/tag/v3.1.6
- https://github.com/fastify/fast-uri/releases/tag/v4.1.3
