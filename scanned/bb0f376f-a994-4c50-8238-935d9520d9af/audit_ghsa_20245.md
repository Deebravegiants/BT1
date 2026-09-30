# [M] Reachable Assertion in rulex

## Summary
Severity: Medium
Advisory: GHSA-8v9w-p43c-r885
CVE: CVE-2022-31100
CWE: CWE-617
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-21
Source: https://github.com/advisories/GHSA-8v9w-p43c-r885
Type: github-advisory

## Affected
- crates.io: `rulex` — affected >=0 <0.4.3

## Details
### Impact
When parsing untrusted rulex expressions, rulex may crash, possibly enabling a Denial of Service attack. This happens when the expression contains a multi-byte UTF-8 code point in a string literal or after a backslash, because rulex tries to slice into the code point and panics as a result.

This is a security concern for you, if
- your service parses untrusted rulex expressions (expressions provided by an untrusted user), and
- your service becomes unavailable when the thread running rulex panics.

### Patches
The crashes are fixed in version **0.4.3**. Affected users are advised to update to this version.

### Workarounds
You can use `catch_unwind` to recover from panics.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [rulex](https://github.com/rulex-rs/rulex/issues)
* Email me at [ludwig.stecher@gmx.de](mailto:ludwig.stecher@gmx.de)

### Credits

Credit for finding these bugs goes to

- [cargo fuzz](https://github.com/rust-fuzz/cargo-fuzz) and [afl.rs](https://github.com/rust-fuzz/afl.rs)
- [evanrichter](https://github.com/evanrichter)
- [ForAllSecure Mayhem](https://forallsecure.com/)

## References
- https://github.com/rulex-rs/rulex/security/advisories/GHSA-8v9w-p43c-r885
- https://nvd.nist.gov/vuln/detail/CVE-2022-31100
- https://github.com/rulex-rs/rulex/commit/fac6d58b25c6f9f8c0a6cdc4dec75b37b219f1d6
- https://github.com/rulex-rs/rulex
- https://rustsec.org/advisories/RUSTSEC-2022-0031.html
