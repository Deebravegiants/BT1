# [C] Vitest Browser: Exposed Browser Mode API Can Proxy CDP and Overwrite Config Files, Leading to RCE

## Summary
Severity: Critical
Advisory: GHSA-g8mr-85jm-7xhm
CVE: CVE-2026-53633
CWE: CWE-749, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-g8mr-85jm-7xhm
Type: github-advisory

## Affected
- npm: `@vitest/browser` — affected >=5.0.0-beta.0 <5.0.0-beta.4
- npm: `@vitest/browser` — affected >=4.0.0 <4.1.8
- npm: `@vitest/browser` — affected >=3.0.0 <3.2.5
- npm: `vite-plus` — affected >=0 <0.1.24

## Details
## Summary

Vitest Browser Mode exposes a `cdp()` API that forwards raw Chrome DevTools Protocol (CDP) methods over the Vitest browser WebSocket RPC. CDP is not gated by `browser.api.allowWrite`, `browser.api.allowExec`, `api.allowWrite`, or `api.allowExec`.

As a result, disabling Browser Mode write and exec operations does not prevent a browser API client from using CDP to perform equivalent actions. In a verified reproduction with `allowWrite: false` and `allowExec: false`, CDP `Page.setDownloadBehavior` set the browser download directory to the project root, and CDP `Runtime.evaluate` downloaded a controlled `vite.config.ts`. Vitest reloaded the changed config and executed attacker-controlled Node.js code.

When the Browser Mode API is also exposed to the network, this becomes remotely exploitable because the generated browser runner page exposes the API token, active session id, project name, and project root path needed to connect to the browser WebSocket API and select the target download directory.

## Impact

This affects Browser Mode projects using a CDP-capable provider, such as Playwright Chromium, when the browser API server is exposed to the network, for example with `--browser.api.host=0.0.0.0`.

In this mode Vitest warns that write and exec operations are disabled by default, but the generated browser runner page exposes enough metadata for a remote client to authenticate to the browser WebSocket API while an active session exists. This includes the browser API token, active session id, project name, and serialized test config including the project root path. The attacker can then call Vitest's CDP RPC and use Chrome's download controls to overwrite `vite.config.ts` in the project root. When Vitest reloads the changed config, attacker-controlled Node.js code executes on the host running Vitest.

The same exposed CDP bridge also allows direct browser-session JavaScript execution through `Runtime.evaluate`. A separate local probe showed that CDP can navigate the browser to a `file://` URL and read rendered file contents, but the primary verified impact is config-file overwrite leading to RCE.

## Reproduction

For a concrete reproduction, start Browser Mode in watch mode using the official Lit example:

```sh
pnpm dlx tiged vitest-dev/vitest/examples/lit vitest-poc
cd vitest-poc
pnpm install
```

Configure the Browser Mode API to listen on all interfaces while explicitly disabling write and exec operations:

```ts
import { playwright } from '@vitest/browser-playwright'
import { defineConfig } from 'vite'

export default defineConfig({
  test: {
    browser: {
      enabled: true,
      provider: playwright(),
      instances: [
        { browser: 'chromium' },
      ],
      api: {
        host: '0.0.0.0',
        allowWrite: false,
        allowExec: false,
      },
    },
  },
})
```

Then start the test server:

```sh
pnpm test
```

Vitest serves the browser runner HTML and WebSocket API at `http://localhost:63315`.

While the browser session is active:

1. Fetch the generated browser runner page:

   ```text
   http://localhost:63315/__vitest_test__/
   ```

2. Extract the embedded browser API token, active session id, project name, and project root:

   - `window.VITEST_API_TOKEN`
   - `__vitest_browser_runner__.sessionId`
   - `__vitest_browser_runner__.config.name`
   - `__vitest_browser_runner__.config.root`

3. Connect to the browser API WebSocket as a tester client:

   ```text
   /__vitest_browser_api__?type=tester&rpcId=<fresh-id>&sessionId=<session-id>&projectName=<project-name>&method=none&token=<token>
   ```

4. Call the `sendCdpEvent` RPC method with:

   ```text
   Page.setDownloadBehavior({
     behavior: "allow",
     downloadPath: __vitest_browser_runner__.config.root
   })
   ```

5. Call `sendCdpEvent` again with `Runtime.evaluate`. The evaluated JavaScript creates a Blob containing a malicious Vite config and clicks an anchor element `<a download="vite.config.ts">`.

6. Observed result:

   - `vite.config.ts` is overwritten with attacker-controlled content.
   - Vitest reloads the changed config.
   - The injected Node.js payload runs on the host.

## References
- https://github.com/vitest-dev/vitest/security/advisories/GHSA-g8mr-85jm-7xhm
- https://nvd.nist.gov/vuln/detail/CVE-2026-53633
- https://github.com/vitest-dev/vitest/pull/10444
- https://github.com/vitest-dev/vitest/pull/10450
- https://github.com/vitest-dev/vitest/pull/10456
- https://github.com/vitest-dev/vitest/commit/385a1aefd4c2bfa5e7d58bf7c6834c929969f2c7
- https://github.com/vitest-dev/vitest/commit/63e3b2eee4d58da56786a6333f517b9b492528c7
- https://github.com/vitest-dev/vitest/commit/e4067b3b150005fd42cf75f994300119245806b9
- https://github.com/vitest-dev/vitest
- https://github.com/vitest-dev/vitest/releases/tag/v3.2.5
- https://github.com/vitest-dev/vitest/releases/tag/v4.1.8
- https://github.com/vitest-dev/vitest/releases/tag/v5.0.0-beta.4
