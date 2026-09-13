# [M] gix-date can create non-utf8 string with `TimeBuf::as_str`

## Summary
Severity: Medium
Advisory: GHSA-6mw6-mj76-grwc
CVE: CVE-2026-0810
CWE: CWE-787
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-6mw6-mj76-grwc
Type: github-advisory

## Affected
- crates.io: `gix-date` — affected >=0 <0.12.0

## Details
The function `gix_date::parse::TimeBuf::as_str` can create an illegal string containing non-utf8 characters. This violates the safety invariant of `TimeBuf` and can lead to undefined behavior when consuming the string.

The bug can be prevented by adding `str::from_utf8` to the function `TimeBuf::write`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-0810
- https://github.com/GitoxideLabs/gitoxide/issues/2305
- https://github.com/GitoxideLabs/gitoxide/pull/2306
- https://github.com/GitoxideLabs/gitoxide/commit/76376ef5e97c63e108db0c9fe2eb096f4bfe70f7
- https://access.redhat.com/security/cve/CVE-2026-0810
- https://bugzilla.redhat.com/show_bug.cgi?id=2427057
- https://github.com/GitoxideLabs/gitoxide
- https://rustsec.org/advisories/RUSTSEC-2025-0140.html
