# [H] Data races in gfwx

## Summary
Severity: High
Advisory: GHSA-xp6v-qx65-4pp7
CVE: CVE-2020-36211
CWE: CWE-662, CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-xp6v-qx65-4pp7
Type: github-advisory

## Affected
- crates.io: `gfwx` — affected >=0 <0.3.0

## Details
In the affected versions of this crate, ImageChunkMut<'_, T> unconditionally implements Send and Sync, allowing to create data races.

This can result in a memory corruption or undefined behavior when non thread-safe types are moved and referenced across thread boundaries.

The flaw was corrected in commit e7fb2f5 by adding T: Send bound to the Send impl and adding T: Sync bound to the Sync impl.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36211
- https://github.com/Devolutions/gfwx-rs/issues/7
- https://github.com/Devolutions/gfwx-rs
- https://rustsec.org/advisories/RUSTSEC-2020-0104.html
