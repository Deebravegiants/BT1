# [C] Shescape: Shell injection via unescaped parentheses on Windows with CMD

## Summary
Severity: Critical
Advisory: GHSA-w4hw-qcx7-56pr
CVE: CVE-2026-73414
CWE: CWE-150, CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-w4hw-qcx7-56pr
Type: github-advisory

## Affected
- npm: `shescape` — affected >=0 <2.1.14
- npm: `shescape` — affected >=3.0.0 <3.0.1

## Details
### Impact

This impacts users of Shescape on Windows that explicitly configure `shell` to CMD, or `true` with the default shell being CMD, using the `escape` and `escapeAll` APIs.

An attacker may be able to achieve shell injection depending on the original command.

```javascript
import * as cp from "node:child_process";
import { Shescape } from "shescape";

// 1. Prerequisites
const options = {
    shell: "cmd.exe",
    // Or
    shell: true, // Only if the default shell is CMD
};

// 2. Payload
const payload = "x) else if a==a (echo y";

// 3. Usage
const shescape = new Shescape(options);
let escapedPayload;

escapedPayload = shescape.escape(payload);
// Or
escapedPayload = shescape.escapeAll([payload]);

// And (example)
const result = cp.execSync(`if defined FALSY (echo ${escapedPayload})`, options);

// 4. Impact
console.log(result.toString());
// Outputs "y" instead of ""

```

### Patches

This bug has been patched in [v2.1.14] and [v3.0.1] which you can upgrade to now.

If you are already using v3 of Shescape, no further changes are required. If you are using v2 of Shescape is recommended to upgrade as this version reaches end-of-life status on 2026-09-28, follow the [migration guide] to upgrade to v3.

No patches will be released for version of Shescape lower than v2.0.0.

### Workarounds

Alternatively, users of Shescape can remove all instances of `(` and `)` from untrusted inputs.

### For more information

- Comment on Pull Request [#2651] for v2 and [#2649] for v3
- Comment on commit [b4b34c3] for v2 and [43d70b5] for v3
- Open an issue at <https://github.com/ericcornelissen/shescape/issues> (New issue > Question)

## References
- https://github.com/ericcornelissen/shescape/security/advisories/GHSA-w4hw-qcx7-56pr
- https://github.com/ericcornelissen/shescape/pull/2649
- https://github.com/ericcornelissen/shescape/pull/2651
- https://github.com/ericcornelissen/shescape/commit/43d70b59d09bbe5c3fd02ef08b3a123e977ed9de
- https://github.com/ericcornelissen/shescape/commit/b4b34c394e7f9da2775bb75381066b9a228c425f
- https://github.com/ericcornelissen/shescape
- https://github.com/ericcornelissen/shescape/blob/dea8893a5877893d8d4923dbf253080e08899e6d/docs/migration.md
- https://github.com/ericcornelissen/shescape/releases/tag/v2.1.14
- https://github.com/ericcornelissen/shescape/releases/tag/v3.0.1
