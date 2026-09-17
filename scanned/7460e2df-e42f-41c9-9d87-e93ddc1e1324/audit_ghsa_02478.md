# [C] Data races in rulinalg

## Summary
Severity: Critical
Advisory: GHSA-q2gj-9r85-p832
CVE: CVE-2020-35879
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-q2gj-9r85-p832
Type: github-advisory

## Affected
- crates.io: `rulinalg` — affected >=0.4.0

## Details
The affected version of rulinalg has incorrect lifetime boundary definitions for RowMut::raw_slice and RowMut::raw_slice_mut. They do not conform with Rust's borrowing rule and allows the user to create multiple mutable references to the same location. This may result in unexpected calculation result and data race if both references are used at the same time.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35879
- https://github.com/AtheMathmo/rulinalg/issues/201
- https://github.com/AtheMathmo/rulinalg
- https://rustsec.org/advisories/RUSTSEC-2020-0023.html
