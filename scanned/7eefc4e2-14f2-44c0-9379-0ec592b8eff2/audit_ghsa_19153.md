# [M] Vitest browser mode serves arbitrary files

## Summary
Severity: Medium
Advisory: GHSA-8gvc-j273-4wm5
CVE: CVE-2025-24963
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-02-04
Source: https://github.com/advisories/GHSA-8gvc-j273-4wm5
Type: github-advisory

## Affected
- npm: `@vitest/browser` — affected >=2.0.4 <2.1.9
- npm: `@vitest/browser` — affected >=3.0.0 <3.0.4

## Details
### Summary
`__screenshot-error` handler on the browser mode HTTP server that responds any file on the file system. Especially if the server is exposed on the network by [`browser.api.host: true`](https://vitest.dev/guide/browser/config.html#browser-api), an attacker can send a request to that handler from remote to get the content of arbitrary files.

### Details
This `__screenshot-error` handler on the browser mode HTTP server responds any file on the file system.
https://github.com/vitest-dev/vitest/blob/f17918a79969d27a415f70431e08a9445b051e45/packages/browser/src/node/plugin.ts#L88-L130

This code was added by https://github.com/vitest-dev/vitest/commit/2d62051f13b4b0939b2f7e94e88006d830dc4d1f.

### PoC
1. Create a directory and change the current directory to that directory
1. Run `npx vitest init browser`
1. Run `npm run test:browser`
2. Run `curl http://localhost:63315/__screenshot-error?file=/path/to/any/file`

### Impact
Users explicitly exposing the browser mode server to the network by [`browser.api.host: true`](https://vitest.dev/guide/browser/config.html#browser-api) may get any files exposed.

## References
- https://github.com/vitest-dev/vitest/security/advisories/GHSA-8gvc-j273-4wm5
- https://nvd.nist.gov/vuln/detail/CVE-2025-24963
- https://github.com/vitest-dev/vitest/commit/2d62051f13b4b0939b2f7e94e88006d830dc4d1f
- https://github.com/vitest-dev/vitest/commit/ed9aeba212df04b83ed01810780663ff2cdd0adf
- https://github.com/vitest-dev/vitest
- https://github.com/vitest-dev/vitest/blob/f17918a79969d27a415f70431e08a9445b051e45/packages/browser/src/node/plugin.ts#L88-L130
- https://vitest.dev/guide/browser/config.html#browser-api
