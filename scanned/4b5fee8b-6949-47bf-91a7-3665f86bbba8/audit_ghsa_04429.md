# [M] hono: Path traversal in `serve-static` on Windows via encoded backslash (`%5C`)

## Summary
Severity: Medium
Advisory: GHSA-wwfh-h76j-fc44
CVE: CVE-2026-54286
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-wwfh-h76j-fc44
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.12.25

## Details
### Summary

On Windows hosts, an encoded backslash (`%5C`) in the request path decodes to `\`, which the Windows path resolver treats as a separator. `serve-static` then resolves a single URL segment such as `admin\secret.txt` into a nested file under the root and serves it, letting an attacker read static files meant to be protected behind prefix-mounted middleware. Directory escape (`..`) remains blocked.

### Details

The router splits paths only on `/`, so `/admin%5Csecret.txt` is one segment and middleware on `/admin/*` does not run. The `serve-static` guard rejects `.`/`..` and consecutive separators but lets a lone `\` through; on Windows the file resolver re-splits it into the protected subtree.

This affects Windows hosts serving static files via the Node, Bun, or Deno adapters that guard a static subtree with prefix-mounted middleware.

### Impact

An unauthenticated attacker can read static files under a middleware-guarded prefix on Windows hosts. The read stays within the configured root; escape outside the root is not possible.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-wwfh-h76j-fc44
- https://nvd.nist.gov/vuln/detail/CVE-2026-54286
- https://github.com/honojs/hono
