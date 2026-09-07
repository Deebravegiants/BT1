# [M] Data races in max7301

## Summary
Severity: Medium
Advisory: GHSA-rmff-f8w9-c9rm
CVE: CVE-2020-36472
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-rmff-f8w9-c9rm
Type: github-advisory

## Affected
- crates.io: `max7301` — affected >=0 <0.2.0

## Details
The `ImmediateIO` and `TransactionalIO` types implement `Sync` for all contained
`Expander<EI>` types regardless of if the `Expander` itself is safe to use
across threads.

As the `IO` types allow retrieving the `Expander`, this can lead to non-thread
safe types being sent across threads as part of the `Expander` leading to data
races.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36472
- https://github.com/edarc/max7301/issues/1
- https://github.com/edarc/max7301/commit/0a1da873ddb29bca926bad8301f8d7ab8aa97c52
- https://github.com/edarc/max7301
- https://rustsec.org/advisories/RUSTSEC-2020-0152.html
