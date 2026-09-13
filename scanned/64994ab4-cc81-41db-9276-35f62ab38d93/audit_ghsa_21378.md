# [H] Inefficient Regular Expression Complexity in shescape 

## Summary
Severity: High
Advisory: GHSA-cr84-xvw4-qx3c
CVE: CVE-2022-25918
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-25
Source: https://github.com/advisories/GHSA-cr84-xvw4-qx3c
Type: github-advisory

## Affected
- npm: `shescape` — affected >=1.5.10 <1.6.1

## Details
### Impact

This impacts users that use shescape to escape arguments:

- for the Unix shell Bash, or any not-officially-supported Unix shell;
- using the `escape` or `escapeAll` functions with the `interpolation` option set to `true`.

An attacker can cause polynomial backtracking in terms of the input string length due to a Regular Expression in shescape that is vulnerable to Regular Expression Denial of Service (ReDoS). Example:

```javascript
import * as shescape from "shescape";

/* 1. Prerequisites */
const options = {
  interpolation: true,
  // and
  shell: "/bin/bash",
  // or
  shell: "some-not-officially-supported-shell",
  // or
  shell: undefined, // Only if the system's default shell is bash or an unsupported shell.
};

/* 2. Attack */
let userInput = '{,'.repeat(150_000); // polynomial backtracking

/* 3. Usage */
shescape.escape(userInput, options);
// or
shescape.escapeAll([userInput], options);
```

### Patches

This bug has been patched in [v1.6.1](https://github.com/ericcornelissen/shescape/releases/tag/v1.6.1) which you can upgrade to now. No further changes required.

### Workarounds

Alternatively, a maximum length can be enforced on input strings to shescape to reduce the impact of the vulnerability. It is not recommended to try and detect vulnerable input strings, as the logic for this may end up being vulnerable to ReDoS itself.

### References

- Shescape commit [552e8ea](https://github.com/ericcornelissen/shescape/commit/552e8eab56861720b1d4e5474fb65741643358f9)
- Shescape Release [v1.6.1](https://github.com/ericcornelissen/shescape/releases/tag/v1.6.1)

### For more information

- Comment on commit [552e8ea](https://github.com/ericcornelissen/shescape/commit/552e8eab56861720b1d4e5474fb65741643358f9)
- Open an issue at [https://github.com/ericcornelissen/shescape/issues](https://github.com/ericcornelissen/shescape/issues?q=is%3Aissue+is%3Aopen) (New issue > Question > Get started)

## References
- https://github.com/ericcornelissen/shescape/security/advisories/GHSA-cr84-xvw4-qx3c
- https://nvd.nist.gov/vuln/detail/CVE-2022-25918
- https://github.com/ericcornelissen/shescape/commit/552e8eab56861720b1d4e5474fb65741643358f9
- https://github.com/ericcornelissen/shescape
- https://github.com/ericcornelissen/shescape/blob/main/src/unix.js%23L52
- https://github.com/ericcornelissen/shescape/releases/tag/v1.6.1
- https://security.snyk.io/vuln/SNYK-JS-SHESCAPE-3061108
