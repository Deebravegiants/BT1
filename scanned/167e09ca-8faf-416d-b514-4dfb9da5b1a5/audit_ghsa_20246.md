# [M] Uncontrolled Recursion in rulex

## Summary
Severity: Medium
Advisory: GHSA-v78m-2q7v-fjqp
CVE: CVE-2022-31099
CWE: CWE-674
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-22
Source: https://github.com/advisories/GHSA-v78m-2q7v-fjqp
Type: github-advisory

## Affected
- crates.io: `rulex` — affected >=0 <0.4.3

## Details
### Impact
When parsing untrusted rulex expressions, the stack may overflow, possibly enabling a Denial of Service attack. This happens when parsing an expression with several hundred levels of nesting, causing the process to abort immediately.

This is a security concern for you, if
- your service parses untrusted rulex expressions (expressions provided by an untrusted user), and
- your service becomes unavailable when the process running rulex aborts due to a stack overflow.

### Patches
The crash is fixed in version **0.4.3**. Affected users are advised to update to this version.

### Workarounds
None.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [rulex](https://github.com/rulex-rs/rulex/issues)
* Email me at [ludwig.stecher@gmx.de](mailto:ludwig.stecher@gmx.de)

### Credits

Credit for finding these bugs goes to

- [evanrichter](https://github.com/evanrichter)
- [ForAllSecure Mayhem](https://forallsecure.com/)
- [cargo fuzz](https://github.com/rust-fuzz/cargo-fuzz) and [afl.rs](https://github.com/rust-fuzz/afl.rs)

## References
- https://github.com/rulex-rs/rulex/security/advisories/GHSA-v78m-2q7v-fjqp
- https://nvd.nist.gov/vuln/detail/CVE-2022-31099
- https://github.com/rulex-rs/rulex/commit/60aa2dc03a22d69c8800fec81f99c96958a11363
- https://github.com/rulex-rs/rulex
- https://rustsec.org/advisories/RUSTSEC-2022-0030.html
