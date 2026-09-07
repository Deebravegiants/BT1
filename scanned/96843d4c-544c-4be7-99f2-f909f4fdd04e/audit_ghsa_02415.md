# [H] XSS in mdBook

## Summary
Severity: High
Advisory: GHSA-gx5w-rrhp-f436
CVE: CVE-2020-26297
CWE: CWE-79
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-gx5w-rrhp-f436
Type: github-advisory

## Affected
- crates.io: `mdBook` — affected >=0.1.4 <0.4.5

## Details
> This is a cross-post of [the official security advisory][ml]. The official post contains a signed version with our PGP key, as well.

[ml]: https://groups.google.com/g/rustlang-security-announcements/c/3-sO6of29O0

The Rust Security Response Working Group was recently notified of a security issue affecting the search feature of mdBook, which could allow an attacker to execute arbitrary JavaScript code on the page.

The CVE for this vulnerability is [CVE-2020-26297](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-26297).

## Overview

The search feature of mdBook (introduced in version 0.1.4) was affected by a cross site scripting vulnerability that allowed an attacker to execute arbitrary JavaScript code on an user's browser by tricking the user into typing a malicious search query, or tricking the user into clicking a link to the search page with the malicious search query prefilled.

mdBook 0.4.5 fixes the vulnerability by properly escaping the search query.

## Mitigations

Owners of websites built with mdBook have to upgrade to mdBook 0.4.5 or greater and rebuild their website contents with it. It's possible to install mdBook 0.4.5 on the local system with:

```
cargo install mdbook --version 0.4.5 --force
```

## Acknowledgements

Thanks to Kamil Vavra for responsibly disclosing the vulnerability to us according to [our security policy](https://www.rust-lang.org/policies/security).

## Timeline of events

All times are listed in UTC.

- 2020-12-30 20:14 - The issue is reported to the Rust Security Response WG
- 2020-12-30 20:32 - The issue is acknowledged and the investigation began
- 2020-12-30 21:21 - Found the cause of the vulnerability and prepared the patch
- 2021-01-04 15:00 - Patched version released and vulnerability disclosed

## References
- https://github.com/rust-lang/mdBook/security/advisories/GHSA-gx5w-rrhp-f436
- https://nvd.nist.gov/vuln/detail/CVE-2020-26297
- https://github.com/rust-lang/mdBook/commit/32abeef088e98327ca0dfccdad92e84afa9d2e9b
- https://github.com/rust-lang/mdBook
- https://github.com/rust-lang/mdBook/blob/master/CHANGELOG.md#mdbook-045
- https://groups.google.com/g/rustlang-security-announcements/c/3-sO6of29O0
- https://rustsec.org/advisories/RUSTSEC-2021-0001.html
