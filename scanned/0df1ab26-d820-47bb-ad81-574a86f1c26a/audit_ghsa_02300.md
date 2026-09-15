# [H] Stack consumption in trust-dns-server

## Summary
Severity: High
Advisory: GHSA-4cww-f7w5-x525
CVE: CVE-2020-35857
CWE: CWE-400
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-4cww-f7w5-x525
Type: github-advisory

## Affected
- crates.io: `trust-dns-server` — affected >=0.16.0 <0.18.1

## Details
There's a stack overflow leading to a crash and potential DOS when processing additional records for return of MX or SRV record types from the server. This is only possible when a zone is configured with a null target for MX or SRV records. Prior to 0.16.0 the additional record processing was not supported by trust-dns-server. There Are no known issues with upgrading from 0.16 or 0.17 to 0.18.1. The remidy should be to upgrade to 0.18.1. If unable to do so, MX, SRV or other record types with a target to the null type, should be avoided.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35857
- https://github.com/bluejekyll/trust-dns/issues/980
- https://github.com/bluejekyll/trust-dns/pull/982
- https://github.com/bluejekyll/trust-dns/commit/8b9eab05795fdc098976262853b2498055c7a8f3
- https://github.com/bluejekyll/trust-dns
- https://rustsec.org/advisories/RUSTSEC-2020-0001.html
