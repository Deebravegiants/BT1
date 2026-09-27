# [M] Data races in magnetic

## Summary
Severity: Medium
Advisory: GHSA-wv4p-jp67-jr97
CVE: CVE-2020-35925
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-wv4p-jp67-jr97
Type: github-advisory

## Affected
- crates.io: `magnetic` — affected >=0 <2.0.1

## Details
Affected versions of this crate unconditionally implemented Sync and Send traits for MPMCConsumer and MPMCProducer types. This allows users to send types that do not implement Send trait across thread boundaries, which can cause a data race. The flaw was corrected in the 2.0.1 release by adding T: Send bound to affected Sync/Send trait implementations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35925
- https://github.com/johnshaw/magnetic/issues/9
- https://github.com/johnshaw/magnetic
- https://rustsec.org/advisories/RUSTSEC-2020-0088.html
