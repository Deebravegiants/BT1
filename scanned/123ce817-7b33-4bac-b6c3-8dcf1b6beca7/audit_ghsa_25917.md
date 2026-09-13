# [H] Rust's regex crate vulnerable to regular expression denial of service

## Summary
Severity: High
Advisory: GHSA-m5pq-gvj9-9vr8
CVE: CVE-2022-24713
CWE: CWE-1333, CWE-400
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-03-08
Source: https://github.com/advisories/GHSA-m5pq-gvj9-9vr8
Type: github-advisory

## Affected
- crates.io: `regex` — affected >=0 <1.5.5

## Details
> This is a cross-post of [the official security advisory][advisory]. The official advisory contains a signed version with our PGP key, as well.

[advisory]: https://groups.google.com/g/rustlang-security-announcements/c/NcNNL1Jq7Yw

The Rust Security Response WG was notified that the `regex` crate did not properly limit the complexity of the regular expressions (regex) it parses. An attacker could use this security issue to perform a denial of service, by sending a specially crafted regex to a service accepting untrusted regexes. No known vulnerability is present when parsing untrusted input with trusted regexes.

This issue has been assigned CVE-2022-24713. The severity of this vulnerability is "high" when the `regex` crate is used to parse untrusted regexes. Other uses of the `regex` crate are not affected by this vulnerability.

## Overview

The `regex` crate features built-in mitigations to prevent denial of service attacks caused by untrusted regexes, or untrusted input matched by trusted regexes. Those (tunable) mitigations already provide sane defaults to prevent attacks. This guarantee is documented and it's considered part of the crate's API.

Unfortunately a bug was discovered in the mitigations designed to prevent untrusted regexes to take an arbitrary amount of time during parsing, and it's possible to craft regexes that bypass such mitigations. This makes it possible to perform denial of service attacks by sending specially crafted regexes to services accepting user-controlled, untrusted regexes.

## Affected versions

All versions of the `regex` crate before or equal to 1.5.4 are affected by this issue. The fix is include starting from  `regex` 1.5.5.

## Mitigations

We recommend everyone accepting user-controlled regexes to upgrade immediately to the latest version of the `regex` crate.

Unfortunately there is no fixed set of problematic regexes, as there are practically infinite regexes that could be crafted to exploit this vulnerability. Because of this, we do not recommend denying known problematic regexes.

## Acknowledgements

We want to thank Addison Crump for responsibly disclosing this to us according to the [Rust security policy](https://www.rust-lang.org/policies/security), and for helping review the fix.

We also want to thank Andrew Gallant for developing the fix, and Pietro Albini for coordinating the disclosure and writing this advisory.

## References
- https://github.com/rust-lang/regex/security/advisories/GHSA-m5pq-gvj9-9vr8
- https://nvd.nist.gov/vuln/detail/CVE-2022-24713
- https://github.com/rust-lang/regex/commit/ae70b41d4f46641dbc45c7a4f87954aea356283e
- https://github.com/rust-lang/regex
- https://groups.google.com/g/rustlang-security-announcements/c/NcNNL1Jq7Yw
- https://lists.debian.org/debian-lts-announce/2022/04/msg00003.html
- https://lists.debian.org/debian-lts-announce/2022/04/msg00009.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JANLZ3JXWJR7FSHE57K66UIZUIJZI67T
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/O3YB7CURSG64CIPCDPNMGPE4UU24AB6H
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PDOWTHNVGBOP2HN27PUFIGRYNSNDTYRJ
- https://rustsec.org/advisories/RUSTSEC-2022-0013.html
- https://security.gentoo.org/glsa/202208-08
- https://security.gentoo.org/glsa/202208-14
- https://www.debian.org/security/2022/dsa-5113
- https://www.debian.org/security/2022/dsa-5118
