# [M] Mutable reference with immutable provenance in image

## Summary
Severity: Medium
Advisory: GHSA-9wgh-vjj7-7433
CVE: CVE-2020-35916
CWE: CWE-400
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-9wgh-vjj7-7433
Type: github-advisory

## Affected
- crates.io: `image` — affected >=0 <0.23.12

## Details
A mutable reference to a struct was constructed by dereferencing a pointer obtained from slice::as_ptr. Instead, slice::as_mut_ptr should have been called on the mutable slice argument. The former performs an implicit reborrow as an immutable shared reference which does not allow writing through the derived pointer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35916
- https://github.com/image-rs/image/issues/1357
- https://github.com/image-rs/image/pull/1358
- https://github.com/image-rs/image/commit/5cbe1e6767d11aff3f14c7ad69a06b04e8d583c7
- https://github.com/image-rs/image
- https://rustsec.org/advisories/RUSTSEC-2020-0073.html
