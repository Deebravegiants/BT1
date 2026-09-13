# [C] When Vitest UI server is listening, arbitrary file can be read and executed

## Summary
Severity: Critical
Advisory: GHSA-5xrq-8626-4rwp
CVE: CVE-2026-47429
CWE: CWE-22, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-5xrq-8626-4rwp
Type: github-advisory

## Affected
- npm: `vitest` — affected >=4.0.0 <4.1.0
- npm: `vitest` — affected >=0 <3.2.6

## Details
### Summary
Arbitrary file can be read on Windows when Vitest UI server is listening, especially when exposed to the network.

### Impact
Only users that match either of the following conditions are affected:

- explicitly exposes the Vitest UI server to the network (using `--api.host` or [`api.host` config option](https://vitest.dev/config/api.html))
- running the Vitest UI or Browser Mode on Windows

### Details
The API handler for `/__vitest_attachment__` uses the deprecated `isFileServingAllowed` incorrectly.
https://github.com/vitest-dev/vitest/blob/eb1abf08573032a532015b999ad3501c5e89e3bb/packages/ui/node/index.ts#L77
The function expects the passed value to use `cleanUrl` after the check before file system related operation.
Because of this, it is possible to bypass the check by `\\?\\..\\`. This is not possible on Linux as Linux errors if a directory named `?` does not exist.

A similar problem exists in other places as well.
- https://github.com/vitest-dev/vitest/blob/eb1abf08573032a532015b999ad3501c5e89e3bb/packages/vitest/src/api/setup.ts#L103-L105
- https://github.com/vitest-dev/vitest/blob/eb1abf08573032a532015b999ad3501c5e89e3bb/packages/vitest/src/api/setup.ts#L119-L121
- https://github.com/vitest-dev/vitest/blob/eb1abf08573032a532015b999ad3501c5e89e3bb/packages/browser/src/node/commands/fs.ts#L10-L11
- https://github.com/vitest-dev/vitest/blob/eb1abf08573032a532015b999ad3501c5e89e3bb/packages/browser/src/node/plugin.ts#L194-L196
- https://github.com/vitest-dev/vitest/blob/eb1abf08573032a532015b999ad3501c5e89e3bb/packages/browser/src/node/rpc.ts#L115-L121

**That said**, this `isFileServingAllowed` check does not actually prevent the API to be abused. Since the API has rerun feature and file write feature, it's possible to run arbitrary script by writing a script as a test file using `saveTestFile` and running it using `rerun`. This means exposing the API / Vitest UI is equivalent to giving script execution access.
On the browser mode side, there're `readFile` / `writeFile` / `saveSnapshotFile`. So exposing the browser mode is equivalent to giving file read / write access.

### PoC
1. Run Vitest UI
2. Get the API token by `curl http://localhost:51204/__vitest__/`
3. Run `curl "http://localhost:51204/__vitest_attachment__?path=C:\\path\\to\\project\\?\\..\\..\\secret.txt&amp;contentType=text/plain&amp;token=$TOKEN"` (TOKEN is the API token)
4. curl shows the content of `secret.txt` that is outside the project directory

### Mitigations

Vitest now ships two configuration flags, [`allowWrite`](https://vitest.dev/config/api.html#api-allowwrite) and [`allowExec`](https://vitest.dev/config/api.html#api-allowexec), that gate the privileged operations exploited by this vulnerability. Both are disabled by default whenever the API server is bound to a non-`localhost` host, ensuring that exposing the server to the network no longer implicitly grants write or execute capabilities to remote clients.

When these flags are disabled, the UI also enters a read-only mode: in-browser code editing and test file execution are turned off, removing the attack surface that allowed remote code execution. Many Browser Mode features are also disabled, like attachments, artifacts or snapshots. See [`browser.api`](https://vitest.dev/config/browser/api.html#api-allowwrite).

Users who require the full interactive UI on a networked host must explicitly opt in by setting `allowWrite` and/or `allowExec` to `true`.

## References
- https://github.com/vitest-dev/vitest/security/advisories/GHSA-5xrq-8626-4rwp
- https://nvd.nist.gov/vuln/detail/CVE-2026-47429
- https://github.com/vitest-dev/vitest/pull/10445
- https://github.com/vitest-dev/vitest/pull/9350
- https://github.com/vitest-dev/vitest/commit/20e00ef7808de6d330c5e2fda530f686e08f1c8d
- https://github.com/vitest-dev/vitest/commit/af88b1f5d82844a4761ea9a977156c98e2b14ca8
- https://github.com/vitest-dev/vitest
- https://github.com/vitest-dev/vitest/blob/eb1abf08573032a532015b999ad3501c5e89e3bb/packages/browser/src/node/commands/fs.ts#L10-L11
- https://github.com/vitest-dev/vitest/blob/eb1abf08573032a532015b999ad3501c5e89e3bb/packages/browser/src/node/plugin.ts#L194-L196
- https://github.com/vitest-dev/vitest/blob/eb1abf08573032a532015b999ad3501c5e89e3bb/packages/browser/src/node/rpc.ts#L115-L121
- https://github.com/vitest-dev/vitest/blob/eb1abf08573032a532015b999ad3501c5e89e3bb/packages/ui/node/index.ts#L77
- https://github.com/vitest-dev/vitest/blob/eb1abf08573032a532015b999ad3501c5e89e3bb/packages/vitest/src/api/setup.ts#L103-L105
- https://github.com/vitest-dev/vitest/blob/eb1abf08573032a532015b999ad3501c5e89e3bb/packages/vitest/src/api/setup.ts#L119-L121
- https://github.com/vitest-dev/vitest/releases/tag/v3.2.5
- https://github.com/vitest-dev/vitest/releases/tag/v4.1.0
