# [M] `idna` accepts Punycode labels that do not produce any non-ASCII when decoded

## Summary
Severity: Medium
Advisory: GHSA-h97m-ww89-6jmq
CVE: CVE-2024-12224
CWE: CWE-1289, CWE-697
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-12-09
Source: https://github.com/advisories/GHSA-h97m-ww89-6jmq
Type: github-advisory

## Affected
- crates.io: `idna` — affected >=0 <1.0.0

## Details
`idna` 0.5.0 and earlier accepts Punycode labels that do not produce any non-ASCII output, which means that either ASCII labels or the empty root label can be masked such that they appear unequal without IDNA processing or when processed with a different implementation and equal when processed with `idna` 0.5.0 or earlier.

Concretely, `example.org` and `xn--example-.org` become equal after processing by `idna` 0.5.0 or earlier. Also, `example.org.xn--` and `example.org.` become equal after processing by `idna` 0.5.0 or earlier.

In applications using `idna` (but not in `idna` itself) this may be able to lead to privilege escalation when host name comparison is part of a privilege check and the behavior is combined with a client that resolves domains with such labels instead of treating them as errors that preclude DNS resolution / URL fetching and with the attacker managing to introduce a DNS entry (and TLS certificate) for an `xn--`-masked name that turns into the name of the target when processed by `idna` 0.5.0 or earlier.

## Remedy

Upgrade to `idna` 1.0.3 or later, if depending on `idna` directly, or to `url` 2.5.4 or later, if depending on `idna` via `url`. (This issue was fixed in `idna` 1.0.0, but versions earlier than 1.0.3 are not recommended for other reasons.)

When upgrading, please take a moment to read about [alternative Unicode back ends for `idna`](https://docs.rs/crate/idna_adapter/latest).

If you are using Rust earlier than 1.81 in combination with SQLx 0.8.2 or earlier, please also read an [issue](https://github.com/servo/rust-url/issues/992) about combining them with `url` 2.5.4 and `idna` 1.0.3.

## Additional information

This issue resulted from `idna` 0.5.0 and earlier implementing the UTS 46 specification literally on this point and the specification having this bug. The specification bug has been fixed in [revision 33 of UTS 46](https://www.unicode.org/reports/tr46/tr46-33.html#Modifications).

## Acknowledgements

Thanks to kageshiron for recognizing the security implications of this behavior.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-12224
- https://bugzilla.mozilla.org/show_bug.cgi?id=1887898
- https://github.com/servo/rust-url
- https://rustsec.org/advisories/RUSTSEC-2024-0421.html
