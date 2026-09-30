# [C] Shescape vulnerable to insufficient escaping of whitespace

## Summary
Severity: Critical
Advisory: GHSA-44vr-rwwj-p88h
CVE: CVE-2022-31180
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-15
Source: https://github.com/advisories/GHSA-44vr-rwwj-p88h
Type: github-advisory

## Affected
- npm: `shescape` — affected >=1.4.0 <1.5.8

## Details
### Impact

This only impacts users that use the `escape` or `escapeAll` functions with the `interpolation` option set to `true`. Example:

```javascript
import cp from "node:child_process";
import * as shescape from "shescape";

// 1. Prerequisites
const options = {
  shell: "bash",
  // Or
  shell: "dash",
  // Or
  shell: "powershell.exe",
  // Or
  shell: "zsh",
  // Or
  shell: undefined, // Only if the default shell is one of the affected shells.
};

// 2. Attack (one of multiple)
const payload = "foo #bar";

// 3. Usage
let escapedPayload;
shescape.escape(payload, { interpolation: true });
// Or
shescape.escapeAll(payload, { interpolation: true });

cp.execSync(`echo Hello ${escapedPayload}!`, options);
// _Output depends on the shell being used_
```

The result is that if an attacker is able to include whitespace in their input they can:

1. Invoke shell-specific behaviour through shell-specific special characters inserted directly after whitespace.
   - Affected shells: _Bash_, _Dash_, _Zsh_, _PowerShell_
2. Invoke shell-specific behaviour through shell-specific special characters inserted or appearing after line terminating characters. 
   - Affected shells: _Bash_
3. Invoke arbitrary commands by inserting a line feed character.
   - Affected Shells: _Bash_, _Dash_, _Zsh_, _PowerShell_
3. Invoke arbitrary commands by inserting a carriage return character.
   - Affected Shells: _PowerShell_

### Patches

Behaviour number 1 has been patched in [v1.5.7] which you can upgrade to now. No further changes are required.

Behaviour number 2, 3, and 4 have been patched in [v1.5.8] which you can upgrade to now. No further changes are required.

### Workarounds

The best workaround is to avoid having to use the `interpolation: true` option - in most cases using an alternative is possible, see [the recipes](https://github.com/ericcornelissen/shescape#recipes) for recommendations.

Alternatively, you can strip all whitespace from user input. Note that this is error prone, for example: for PowerShell this requires stripping `'\u0085'` which is not included in JavaScript's definition of `\s` for Regular Expressions.

### References

- https://github.com/ericcornelissen/shescape/pull/322
- https://github.com/ericcornelissen/shescape/pull/324
- https://github.com/ericcornelissen/shescape/pull/332
- https://github.com/ericcornelissen/shescape/releases/tag/v1.5.7
- https://github.com/ericcornelissen/shescape/releases/tag/v1.5.8

### For more information

- Comment on:
  - For behaviour 1 (PowerShell): https://github.com/ericcornelissen/shescape/pull/322
  - For behaviour 1 (Bash, Dash, Zsh): https://github.com/ericcornelissen/shescape/pull/324
  - For behaviour 2, 3, 4 (_any shell_): https://github.com/ericcornelissen/shescape/pull/332
- Open an issue at https://github.com/ericcornelissen/shescape/issues (_New issue_ > _Question_ > _Get started_)
- If you're missing CMD from this advisory, see https://github.com/ericcornelissen/shescape/security/advisories/GHSA-jjc5-fp7p-6f8w

[v1.5.7]: https://github.com/ericcornelissen/shescape/releases/tag/v1.5.7
[v1.5.8]: https://github.com/ericcornelissen/shescape/releases/tag/v1.5.8

## References
- https://github.com/ericcornelissen/shescape/security/advisories/GHSA-44vr-rwwj-p88h
- https://nvd.nist.gov/vuln/detail/CVE-2022-31180
- https://github.com/ericcornelissen/shescape/pull/322
- https://github.com/ericcornelissen/shescape/pull/324
- https://github.com/ericcornelissen/shescape/pull/332
- https://github.com/ericcornelissen/shescape
- https://github.com/ericcornelissen/shescape/releases/tag/v1.5.7
- https://github.com/ericcornelissen/shescape/releases/tag/v1.5.8
