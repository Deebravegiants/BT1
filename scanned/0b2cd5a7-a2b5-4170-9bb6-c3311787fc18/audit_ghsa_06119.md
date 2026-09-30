# [H] fast-uri vulnerable to host confusion via backslash authority introducer

## Summary
Severity: High
Advisory: GHSA-7p8r-x3mc-p8w7
CVE: CVE-2026-18446
CWE: CWE-436
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-7p8r-x3mc-p8w7
Type: github-advisory

## Affected
- npm: `fast-uri` — affected >=0 <2.4.4
- npm: `fast-uri` — affected >=3.0.0 <3.1.5
- npm: `fast-uri` — affected >=4.0.0 <4.1.2

## Details
### Impact

`fast-uri` v4.1.1 and earlier require a literal `//` to recognize a URI authority, so a reference that uses `\\`, `/\`, or `\/` as the authority introducer (in place of `//`, after an optional scheme) is parsed with no authority: the sequence and everything after it fold into the path. Node's native WHATWG `URL` (used by `fetch()`, `undici`, and Node's `http`/`https` clients) instead treats `\` as interchangeable with `/` for special schemes (`http`, `https`, `ws`, `wss`, `ftp`, `file`), so the two parsers extract different hosts from the same input.

For example, `fast-uri` resolves `\\evil.com/path` against base `https://allowed.com/` to `https://allowed.com/%5C%5Cevil.com/path` (confined to the trusted host), while Node's WHATWG URL resolves the same reference to `https://evil.com/path`.

Applications that use `fast-uri` to enforce host-based policy (allowlists, denylists, loopback/SSRF filtering, redirect validation, outbound proxy routing) before passing the same URL into Node's URL or `fetch()` consumers see a policy/use desync and can be steered to an unintended destination.

### Patches

Upgrade to `fast-uri` v4.1.2, v3.1.5, v2.4.4.

### Workarounds

None. Upgrade to the patched version.

## References
- https://github.com/fastify/fast-uri/security/advisories/GHSA-7p8r-x3mc-p8w7
- https://nvd.nist.gov/vuln/detail/CVE-2026-18446
- https://github.com/fastify/fast-uri/commit/f3c6c905f47831007490f466c5945012e905cc52
- https://cna.openjsf.org/security-advisories.html
- https://github.com/fastify/fast-uri
- https://github.com/fastify/fast-uri/releases/tag/v4.1.2
