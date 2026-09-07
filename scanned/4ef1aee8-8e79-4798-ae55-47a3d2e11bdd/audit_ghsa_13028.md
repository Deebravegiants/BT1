# [H] Shescape on Windows escaping may be bypassed in threaded context

## Summary
Severity: High
Advisory: GHSA-j55r-787p-m549
CVE: CVE-2023-40185
CWE: CWE-150
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2023-08-22
Source: https://github.com/advisories/GHSA-j55r-787p-m549
Type: github-advisory

## Affected
- npm: `shescape` — affected >=0 <1.7.4

## Details
### Impact

This may impact users that use Shescape on Windows in a threaded context (e.g. using [Worker threads](https://nodejs.org/api/worker_threads.html)). The vulnerability can result in Shescape escaping (or quoting) for the wrong shell, thus allowing attackers to bypass protections depending on the combination of expected and used shell.

This snippet demonstrates a vulnerable use of Shescape:

```javascript
// vulnerable.js

import { exec } from "node:child_process";
import { Worker, isMainThread } from 'node:worker_threads';

import * as shescape from "shescape";

if (isMainThread) {
  // 1. Something like a worker thread must be used. The reason being that they
  // unexpectedly change environment variable names on Windows.
  new Worker("./vulnerable.js");
} else {
  // 2. Example configuration that's problematic. In this setup example the
  // expected default system shell is CMD. We configure the use of PowerShell.
  // Shescape will fail to look up PowerShell and default to escaping for CMD
  // instead, resulting in the vulnerability.
  const options = {
    shell: "powershell",
    interpolation: true,
  };

  // 3. Using shescape to protect against attacks, this is correct.
  const escaped = shescape.escape("&& ls", options);

  // 4. Invoking a command with the escaped user input, this is vulnerable in
  // this case.
  exec(`echo Hello ${escaped}`, options, (error, stdout) => {
    if (error) {
      console.error(`An error occurred: ${error}`);
    } else {
      console.log(stdout);
    }
  });
}
```

### Patches

This bug has been patched in [v1.7.4](https://github.com/ericcornelissen/shescape/releases/tag/v1.7.4) which you can upgrade to now. No further changes are required.

### Workarounds

If you are impacted there is no workaround possible.

### References

- Shescape Pull Request [#1142](https://github.com/ericcornelissen/shescape/pull/1142)
- Shescape commit [`0b976da`](https://github.com/ericcornelissen/shescape/commit/0b976dab645abf45ffd85e74a8c6e51ee2f42d63)
- Shescape release [v1.7.4](https://github.com/ericcornelissen/shescape/releases/tag/v1.7.4)

### For more information

- Comment on Pull Request [#1142](https://github.com/ericcornelissen/shescape/pull/1142)
- Comment on commit [`0b976da`](https://github.com/ericcornelissen/shescape/commit/0b976dab645abf45ffd85e74a8c6e51ee2f42d63)
- Open an issue at [https://github.com/ericcornelissen/shescape/issues](https://github.com/ericcornelissen/shescape/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc) (New issue > Question > Get started)

## References
- https://github.com/ericcornelissen/shescape/security/advisories/GHSA-j55r-787p-m549
- https://nvd.nist.gov/vuln/detail/CVE-2023-40185
- https://github.com/ericcornelissen/shescape/pull/1142
- https://github.com/ericcornelissen/shescape/commit/0b976dab645abf45ffd85e74a8c6e51ee2f42d63
- https://github.com/ericcornelissen/shescape
- https://github.com/ericcornelissen/shescape/releases/tag/v1.7.4
