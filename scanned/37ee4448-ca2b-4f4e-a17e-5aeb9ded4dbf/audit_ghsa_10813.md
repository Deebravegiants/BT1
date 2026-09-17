# [M] smol-toml: Denial of Service via TOML documents containing thousands of consecutive commented lines

## Summary
Severity: Medium
Advisory: GHSA-v3rj-xjv7-4jmq
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-v3rj-xjv7-4jmq
Type: github-advisory

## Affected
- npm: `smol-toml` — affected >=0 <1.6.1

## Details
### Summary
An attacker can send a maliciously crafted TOML to cause the parser to crash, because of a stack overflow caused by thousands of consecutive commented lines.

The library uses recursion internally while parsing to skip over commented lines, which can be exploited to crash an application that is processing arbitrary TOML documents.

### Proof of concept
```js
require("smol-toml").parse('# comment\n'.repeat(8000) + 'key = "value"')
```

### Impact
Applications which parse arbitrary TOML documents may suffer availability issues if they receive malicious input. If uncaught, the crash may cause the application itself to crash. The impact is deemed minor, as the function is already likely to throw errors on invalid input. Downstream users are supposed to properly handle errors in such situations.

Due to the design of most JavaScript runtimes, the uncontrolled recursion does not lead to excessive memory usage and the execution is quickly aborted.

As a reminder, it is **strongly** advised when working with untrusted user input to expect errors to occur and to appropriately catch them.

### Patches
Version 1.6.1 uses a different approach for parsing comments, which no longer involves recursion.

### Workarounds
Wrap all invocations of `parse` and `stringify` in a try/catch block when dealing with untrusted user input.

## References
- https://github.com/squirrelchat/smol-toml/security/advisories/GHSA-v3rj-xjv7-4jmq
- https://github.com/squirrelchat/smol-toml
- https://github.com/squirrelchat/smol-toml/releases/tag/v1.6.1
