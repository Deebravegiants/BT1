# [H] Shescape prior to 1.5.8 vulnerable to insufficient escaping of line feeds for CMD

## Summary
Severity: High
Advisory: GHSA-jjc5-fp7p-6f8w
CVE: CVE-2022-31179
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:H (CVSS_V3)
Published: 2022-07-15
Source: https://github.com/advisories/GHSA-jjc5-fp7p-6f8w
Type: github-advisory

## Affected
- npm: `shescape` — affected >=0 <1.5.8

## Details
### Impact

This impacts users that use Shescape (any API function) to escape arguments for **cmd.exe** on **Windows**. An attacker can omit all arguments following their input by including a line feed character (`'\n'`) in the payload. Example:

```javascript
import cp from "node:child_process";
import * as shescape from "shescape";

// 1. Prerequisites
const options = {
  shell: "cmd.exe",
};

// 2. Attack
const payload = "attacker\n";

// 3. Usage
let escapedPayload;
escapedPayload = shescape.escape(payload, options);
// Or
escapedPayload = shescape.escapeAll([payload], options)[0];
// Or
escapedPayload = shescape.quote(payload, options);
// Or
escapedPayload = shescape.quoteAll([payload], options)[0];

cp.execSync(`echo Hello ${escapedPayload}! How are you doing?`, options);
// Outputs:  "Hello attacker"
```

> **Note**: `execSync` is just illustrative here, all of `exec`, `execFile`, `execFileSync`, `fork`, `spawn`, and `spawnSync` can be attacked using a line feed character if CMD is the shell being used.

### Patches

This bug has been patched in [v1.5.8] which you can upgrade to now. No further changes are required.

### Workarounds

Alternatively, line feed characters (`'\n'`) can be stripped out manually or the user input can be made the last argument (this only limits the impact).

### References

- https://github.com/ericcornelissen/shescape/pull/332
- https://github.com/ericcornelissen/shescape/releases/tag/v1.5.8

### For more information

If you have any questions or comments about this advisory:

- Comment on https://github.com/ericcornelissen/shescape/pull/332
- Open an issue at https://github.com/ericcornelissen/shescape/issues (_New issue_ > _Question_ > _Get started_)

[v1.5.8]: https://github.com/ericcornelissen/shescape/releases/tag/v1.5.8

## References
- https://github.com/ericcornelissen/shescape/security/advisories/GHSA-jjc5-fp7p-6f8w
- https://nvd.nist.gov/vuln/detail/CVE-2022-31179
- https://github.com/ericcornelissen/shescape/pull/332
- https://github.com/ericcornelissen/shescape/commit/aceea7358f7222984e21260381ebc5ec4543b76f
- https://github.com/ericcornelissen/shescape
- https://github.com/ericcornelissen/shescape/releases/tag/v1.5.8
