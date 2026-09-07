# [C] Double-free in id-map

## Summary
Severity: Critical
Advisory: GHSA-vfqx-hv88-f9cv
CVE: CVE-2021-30456
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-vfqx-hv88-f9cv
Type: github-advisory

## Affected
- crates.io: `id-map` — affected >=0

## Details
A double free can occur in get_or_insert upon a panic of a user-provided f function. get_or_insert reserves space for a value, before calling the user provided insertion function f. If the function f panics then uninitialized or previously freed memory can be dropped.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-30456
- https://github.com/andrewhickman/id-map/issues/3
- https://github.com/andrewhickman/id-map
- https://rustsec.org/advisories/RUSTSEC-2021-0052.html
