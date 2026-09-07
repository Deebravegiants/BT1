# [M] scalarmult() vulnerable to degenerate public keys

## Summary
Severity: Medium
Advisory: GHSA-2wc6-2rcj-8v76
CVE: CVE-2017-1000168
CWE: CWE-1240
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-2wc6-2rcj-8v76
Type: github-advisory

## Affected
- crates.io: `sodiumoxide` — affected >=0 <0.0.14

## Details
The scalarmult() function included in previous versions of this crate accepted all-zero public keys, for which the resulting Diffie-Hellman shared secret will always be zero regardless of the private key used.

This issue was fixed by checking for this class of keys and rejecting them if they are used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000168
- https://github.com/dnaq/sodiumoxide/issues/154
- https://github.com/sodiumoxide/sodiumoxide/commit/24c7a5550807ac8a09648b5878f19d14c3a69135
- https://github.com/sodiumoxide/sodiumoxide
- https://rustsec.org/advisories/RUSTSEC-2017-0001.html
