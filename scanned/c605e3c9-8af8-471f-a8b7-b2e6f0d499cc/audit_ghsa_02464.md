# [H] Integer underflow in untrusted

## Summary
Severity: High
Advisory: GHSA-wq8f-46ww-6c2h
CVE: CVE-2018-20989
CWE: CWE-191
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-wq8f-46ww-6c2h
Type: github-advisory

## Affected
- crates.io: `untrusted` — affected >=0 <0.6.2

## Details
A mistake in error handling in untrusted before 0.6.2 could lead to an integer underflow and panic if a user of the crate didn't properly check for errors returned by untrusted. Combination of these two programming errors (one in untrusted and another by user of this crate) could lead to a panic and maybe a denial of service of affected software. The error in untrusted is fixed in release 0.6.2 released 2018-06-21. It's also advisable that users of untrusted check for their sources for cases where errors returned by untrusted are not handled correctly.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20989
- https://github.com/briansmith/untrusted/pull/20
- https://github.com/briansmith/untrusted
- https://rustsec.org/advisories/RUSTSEC-2018-0001.html
