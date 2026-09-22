# [H] Exposure of uninitialized memory in memoffset

## Summary
Severity: High
Advisory: GHSA-rh89-x75f-rh3c
CVE: CVE-2019-15553
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-rh89-x75f-rh3c
Type: github-advisory

## Affected
- crates.io: `memoffset` — affected >=0 <0.5.0

## Details
Affected versions of this crate caused traps and/or memory unsafety by zero-initializing references. They also could lead to uninitialized memory being dropped if the field for which the offset is requested was behind a deref coercion, and that deref coercion caused a panic. The flaw was corrected by using MaybeUninit.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15553
- https://github.com/Gilnaa/memoffset/issues/9#issuecomment-505461490
- https://github.com/Gilnaa/memoffset
- https://rustsec.org/advisories/RUSTSEC-2019-0011.html
