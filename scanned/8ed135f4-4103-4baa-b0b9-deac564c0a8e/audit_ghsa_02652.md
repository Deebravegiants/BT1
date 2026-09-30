# [C] Double free in toodee

## Summary
Severity: Critical
Advisory: GHSA-wcvp-r8j8-47pc
CVE: CVE-2021-28028
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-wcvp-r8j8-47pc
Type: github-advisory

## Affected
- crates.io: `toodee` — affected >=0 <0.3.0

## Details
When inserting rows from an iterator at a particular index, toodee would shift items over, duplicating their ownership. The space reserved for the new elements was based on the len() returned by the ExactSizeIterator.

This could result in elements in the array being freed twice if the iterator panics. Uninitialized or previously freed elements could also be exposed if the len() didn't match the number of elements.

These issues were fixed in commit `ced70c17` by temporarily setting the length of the array smaller while processing it and adding assertions on the number of elements returned by the iterator.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28028
- https://github.com/antonmarsden/toodee/issues/13
- https://github.com/antonmarsden/toodee/commit/ced70c172486fb4827c172cd8238053df3d1dcdb
- https://github.com/antonmarsden/toodee
- https://rustsec.org/advisories/RUSTSEC-2021-0028.html
