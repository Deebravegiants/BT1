# [C] lz4-sys vulnerable to memory corruption via issue in liblz4

## Summary
Severity: Critical
Advisory: GHSA-9q5j-jm53-v7vr
CWE: CWE-190, CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-01
Source: https://github.com/advisories/GHSA-9q5j-jm53-v7vr
Type: github-advisory

## Affected
- crates.io: `lz4-sys` — affected >=0 <1.9.4

## Details
lz4-sys up to v1.9.3 bundles a version of liblz4 that is vulnerable to
[CVE-2021-3520](https://nvd.nist.gov/vuln/detail/CVE-2021-3520).

Attackers could craft a payload that triggers an integer overflow upon
decompression, causing an out-of-bounds write.

The flaw has been corrected in version v1.9.4 of liblz4, which is included
in lz4-sys 1.9.4.

## References
- https://github.com/lz4/lz4/pull/972
- https://rustsec.org/advisories/RUSTSEC-2022-0051.html
