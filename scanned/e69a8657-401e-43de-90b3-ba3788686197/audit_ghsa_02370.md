# [H] Improper Input Validation in cookie

## Summary
Severity: High
Advisory: GHSA-vjrq-cg9x-rfjp
CVE: CVE-2017-18589
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-vjrq-cg9x-rfjp
Type: github-advisory

## Affected
- crates.io: `cookie` — affected >=0 <0.7.6

## Details
Affected versions of this crate use the time crate and the method Duration::seconds to parse the Max-Age duration cookie setting. This method will panic if the value is greater than 2^64/1000 and less than or equal to 2^64, which can result in denial of service for a client or server.

This flaw was corrected by explicitly checking for the Max-Age being in this integer range and clamping the value to the maximum duration value.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18589
- https://github.com/SergioBenitez/cookie-rs/pull/86
- https://github.com/SergioBenitez/cookie-rs/commit/ee18b79fbf0903b73da525d302b09448009e0050
- https://github.com/alexcrichton/cookie-rs
- https://rustsec.org/advisories/RUSTSEC-2017-0005.html
