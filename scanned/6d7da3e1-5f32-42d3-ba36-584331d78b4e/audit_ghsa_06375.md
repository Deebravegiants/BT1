# [H] Orval: Generation-time SSRF + remote/local file inclusion via unrestricted $ref

## Summary
Severity: High
Advisory: GHSA-cxq5-97v7-87j8
CVE: CVE-2026-62680
CWE: CWE-22, CWE-829, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-cxq5-97v7-87j8
Type: github-advisory

## Affected
- npm: `orval` — affected >=0 <8.22.0

## Details
### Summary

Orval resolves OpenAPI `$ref`s by fetching remote `http(s)` URLs and reading local files (including
absolute / out-of-tree paths), inlining the referenced schema into the generated client. Running
`orval` on a spec whose `$ref` points at an attacker/internal URL or an arbitrary local file yields
SSRF, remote file inclusion, and local file inclusion. Verified on 8.19.0. This is a different class
from Orval's published output-injection CVEs (CVE-2026-22785/23947/24132/25141), none of which covers
the `$ref` resolver.

### Details

- `$ref: http://attacker/internal-evil.json#/...` → build host fetches (SSRF) and inlines the remote
  schema (RFI); confirmed property `REMOTE_ORVAL_PROP` in the generated client.
- `$ref: /abs/path.json#/...` or `../../secret.json#/...` → out-of-tree local file read + inlined (LFI).

No RCE: on 8.19.0 the description JSDoc is escaped (`*/`->`*\/`, the published fix), so `$ref` content
cannot break out into code. The chain stops at SSRF + RFI + LFI.

Fix: don't resolve remote `$ref`s by default (opt-in + host allowlist); confine local `$ref`
resolution to the input directory tree (reject absolute paths and `../` escapes).

### PoC

`reproduce.sh` attached: confirms LFI (out-of-tree read), SSRF (listener hit), RFI (remote schema
inlined). Verified on Orval 8.19.0.

### Impact

Build-time SSRF from the developer or CI host, disclosure of arbitrary local files, and inclusion of untrusted remote content, from running the generator on an attacker-controlled or attacker-influenced OpenAPI description. No code execution (output escaping is in place post the earlier fixes).

## References
- https://github.com/orval-labs/orval/security/advisories/GHSA-cxq5-97v7-87j8
- https://nvd.nist.gov/vuln/detail/CVE-2026-62680
- https://github.com/orval-labs/orval/pull/3692
- https://github.com/orval-labs/orval/pull/3723
- https://github.com/orval-labs/orval/commit/23786c056f4eba38c02bf2968677988dbbe4de10
- https://github.com/orval-labs/orval/commit/8ef1bfdf3f9bcaf9dabfbe2e42887f1c0e159ab6
- https://github.com/orval-labs/orval
- https://github.com/orval-labs/orval/releases/tag/v8.22.0
