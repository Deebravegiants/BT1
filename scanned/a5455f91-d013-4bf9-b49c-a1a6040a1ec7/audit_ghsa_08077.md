# [H] hexchat crate has a Use After Free vulnerability

## Summary
Severity: High
Advisory: GHSA-x43w-ph7m-pfjx
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-x43w-ph7m-pfjx
Type: github-advisory

## Affected
- crates.io: `hexchat` — affected >=0

## Details
All versions of this crate have function `deregister_command` which can result in use after free. This is unsound.

In addition, all versions since 0.3.0 have "safe" macros, which are documented as unsafe to use in threads.

In addition, the `hexchat` crate is no longer actively maintained.  If users rely on this crate, consider switching to an alternative.

## References
- https://github.com/pie-flavor/hexchat-rs/issues/3
- https://github.com/pie-flavor/hexchat-rs
- https://rustsec.org/advisories/RUSTSEC-2025-0153.html
