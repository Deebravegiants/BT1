# [C] Zalgo-like output that crashes the server

## Summary
Severity: Critical
Advisory: GHSA-2w8g-m5j8-7m87
Ecosystem: npm
Published: 2022-01-12
Source: https://github.com/advisories/GHSA-2w8g-m5j8-7m87
Type: github-advisory

## Affected
- npm: `@soketi/soketi` — affected >=0 <0.26.1

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

[`colors`](https://npmjs.com/package/colors) package caused zalgo-like output (see https://github.com/soketi/soketi/issues/276, https://github.com/Marak/colors.js/issues/289), breaking the servers.

**Only NPM users that recently upgraded or installed the NPM package are affected.**

Docker users seem to not be affected as the dependencies were bundled at the time of the build, which were tested.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Latest patch. `0.26.1` to be exact at the time of writing.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

You cannot get around this as it's related to dependencies.

### References
_Are there any links users can visit to find out more?_

- https://github.com/Marak/colors.js/issues/289

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the issues board](https://github.com/soketi/soketi/issues)
* Email us at [alex@renoki.org](mailto:alex@renoki.org)

## References
- https://github.com/soketi/soketi/security/advisories/GHSA-2w8g-m5j8-7m87
