# [H] fast-uri vulnerable to host confusion via skipped IDN canonicalization on scheme-relative references

## Summary
Severity: High
Advisory: GHSA-5jgf-p345-68v8
CVE: CVE-2026-75931
CWE: CWE-436
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-5jgf-p345-68v8
Type: github-advisory

## Affected
- npm: `fast-uri` — affected >=2.4.2 <2.4.5
- npm: `fast-uri` — affected >=3.1.3 <3.1.6
- npm: `fast-uri` — affected >=4.0.1 <4.1.3

## Details
### Impact

`fast-uri` canonicalizes a host to its ASCII form only when the input carries an explicit scheme. When `resolve()` resolves a scheme-relative reference (`//host/`) against a scheme-bearing base, it still emits the host verbatim even though the effective scheme is known, so re-parsing the resolved URI yields a different host than the one `resolve()` returned. An application that resolves an untrusted reference with `fast-uri` and then checks or routes on the resulting host can make a policy decision on one host and reach another. This is an incomplete-fix variant of CVE-2026-13676, whose IDN canonicalization was applied only to the scheme-bearing form.

### Patches

Upgrade to `fast-uri` 2.4.5, 3.1.6, or 4.1.3. `resolve()` now canonicalizes the host once the effective scheme is known, and fails closed if a raw non-ASCII host cannot be converted.

### Workarounds

Resolve scheme-relative references against a base that carries a scheme before performing any host-policy or origin check.

## References
- https://github.com/fastify/fast-uri/security/advisories/GHSA-5jgf-p345-68v8
- https://nvd.nist.gov/vuln/detail/CVE-2026-75931
- https://github.com/fastify/fast-uri/commit/0256bc8d1f28b5d0ac657faf67e2411a189dfcb5
- https://github.com/fastify/fast-uri/commit/444ecdad447db2cc23c4d422acc6f0daa6fa8eef
- https://github.com/fastify/fast-uri/commit/4e4ebd8b245f6ca16e448203559eea3e545453a3
- https://cna.openjsf.org/security-advisories.html
- https://github.com/fastify/fast-uri
- https://github.com/fastify/fast-uri/releases/tag/v2.4.5
- https://github.com/fastify/fast-uri/releases/tag/v3.1.6
- https://github.com/fastify/fast-uri/releases/tag/v4.1.3
