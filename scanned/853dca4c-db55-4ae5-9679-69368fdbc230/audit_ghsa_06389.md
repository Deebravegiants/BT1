# [H] fast-uri vulnerable to server-side request forgery via repeated hostname percent-decoding

## Summary
Severity: High
Advisory: GHSA-fph4-wmhf-6fwf
CVE: CVE-2026-75899
CWE: CWE-174, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-fph4-wmhf-6fwf
Type: github-advisory

## Affected
- npm: `fast-uri` — affected >=2.4.1 <2.4.5
- npm: `fast-uri` — affected >=3.1.2 <3.1.6
- npm: `fast-uri` — affected >=4.0.0 <4.1.3

## Details
### Impact

`fast-uri` decodes a hostname's percent escapes twice in a single `normalize()` or `resolve()` call: once during parsing and again during authority recomposition. A nested percent-encoded host therefore survives the first decode and is turned into a live destination by the second, so `normalize('http://%256c%256f%2563%2561%256c%2568%256f%2573%2574/')` returns `http://localhost/`. Applications that normalize or resolve an untrusted URI before an SSRF check, redirect validation, or host allowlist can be steered to a different destination, including internal addresses such as loopback or a cloud metadata endpoint, than the encoded input appeared to contain. This is an incomplete-fix variant of CVE-2026-6322, whose encoded-authority-delimiter fix introduced the second decode.

### Patches

Fixed in `fast-uri` 2.4.5, 3.1.6, and 4.1.3.

### Workarounds

Reject untrusted URIs whose host component contains an encoded percent sign (`%25`) before passing them to `normalize()` or `resolve()`.

## References
- https://github.com/fastify/fast-uri/security/advisories/GHSA-fph4-wmhf-6fwf
- https://nvd.nist.gov/vuln/detail/CVE-2026-75899
- https://github.com/fastify/fast-uri/commit/2642290672e7211c990aaed3749c2ce667d0af4f
- https://github.com/fastify/fast-uri/commit/8c15dbe94ec50bb8e595791ebb42c35cef0fd304
- https://github.com/fastify/fast-uri/commit/ae92a4c5d8c4b6c9e447f048d5fcbde7eebd5514
- https://cna.openjsf.org/security-advisories.html
- https://github.com/fastify/fast-uri
- https://github.com/fastify/fast-uri/releases/tag/v2.4.5
- https://github.com/fastify/fast-uri/releases/tag/v3.1.6
- https://github.com/fastify/fast-uri/releases/tag/v4.1.3
