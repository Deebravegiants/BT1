# [M] Vitest: Path Traversal / Arbitrary File Read via @vitest/mocker Redirect Mock

## Summary
Severity: Medium
Advisory: CVE-2026-84373
Aliases: GHSA-82fw-gwwq-j7x9
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-84373
Type: osv

## Details
Vitest is a testing framework powered by Vite. From 2.1.0 until 4.1.11 and 5.0.0-rc.2, the public mockerPlugin and standalone interceptorPlugin exports in packages/mocker/src/node/interceptorPlugin.ts register the vitest:interceptor:register handler on Vite's unauthenticated HMR WebSocket without validating redirect targets against the file-serving allowlist. The implementation processes event.redirect without enforcing server.fs.allow and server.fs.deny through isFileLoadingAllowed. A remote client that can reach an exposed development server can submit an opaque URL scheme preserving .. segments, causing join(server.config.root, redirectUrl.pathname) to resolve outside the project root. The plugin's load hook then returns readFile(mock.redirect, 'utf-8') as module source, disclosing local files readable by the dev-server process. Vitest browser mode uses a token-authenticated RPC and is not remotely unauthenticated by default, although the same boundary check was missing on that path. This issue is fixed in versions 4.1.11 and 5.0.0-rc.2.

## References
- https://github.com/vitest-dev/vitest/releases/tag/v4.1.11
- https://github.com/vitest-dev/vitest/releases/tag/v5.0.0-rc.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84373.json
- https://github.com/vitest-dev/vitest/security/advisories/GHSA-82fw-gwwq-j7x9
- https://nvd.nist.gov/vuln/detail/CVE-2026-84373
- https://github.com/vitest-dev/vitest/commit/51edf2b072902aec6d30c90ebaafd8f121c6f9d8
- https://github.com/vitest-dev/vitest/commit/8ff9b9a9efca7c6cfd5243569440de8d7a33aec4
- https://github.com/vitest-dev/vitest/commit/fe5a11d3ceac5ec10d6d7d21a46d4caca132c48f
- https://github.com/vitest-dev/vitest/pull/10972
- https://github.com/vitest-dev/vitest/pull/10974
