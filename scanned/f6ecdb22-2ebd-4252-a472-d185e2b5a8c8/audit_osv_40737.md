# [M] Nx: `nx graph` dev server permissive CORS policy

## Summary
Severity: Medium
Advisory: CVE-2026-54753
Aliases: GHSA-g2r8-wvmj-jf5w
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:L/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-54753
Type: osv

## Details
Nx is a monorepo solution for TypeScript and polyglot codebases. From 17.0.4 until 22.7.2 and 23.0.0-beta.2, the local HTTP server started by nx graph sent Access-Control-Allow-Origin: * on every response, letting any website a developer visited read the server's responses cross-origin — including the full project graph and the output of the /help endpoint, which runs a target's configured help command. The practical impact is typically cross-origin information disclosure, but can be arbitrary command injection in rare cases. This vulnerability is fixed in 22.7.2 and 23.0.0-beta.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54753.json
- https://github.com/nrwl/nx/security/advisories/GHSA-g2r8-wvmj-jf5w
- https://nvd.nist.gov/vuln/detail/CVE-2026-54753
- https://github.com/nrwl/nx/pull/35494
