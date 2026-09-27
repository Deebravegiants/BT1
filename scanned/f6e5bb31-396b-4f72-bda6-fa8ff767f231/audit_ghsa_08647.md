# [M] hickory-proto vulnerable to CPU exhaustion during message encoding due to O(n²) name compression

## Summary
Severity: Medium
Advisory: GHSA-q2qq-hmj6-3wpp
CWE: CWE-407, CWE-770
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-q2qq-hmj6-3wpp
Type: github-advisory

## Affected
- crates.io: `hickory-proto` — affected >=0.3.1 <0.26.1

## Details
During message encoding, `hickory-proto`'s `BinEncoder` stores pointers to labels that are candidates for name compression in a `Vec<(usize, Vec<u8>)>`. The name compression logic then searches for matches with a linear scan.

A malicious message with many records can both introduce many candidate labels, and invoke this linear scan many times. This can amplify CPU exhaustion in DoS attacks.

This is similar to [CVE-2024-8508](https://www.nlnetlabs.nl/downloads/unbound/CVE-2024-8508.txt).

### Reporter

Qifan Zhang, Palo Alto Networks

## References
- https://github.com/hickory-dns/hickory-dns/security/advisories/GHSA-q2qq-hmj6-3wpp
- https://github.com/hickory-dns/hickory-dns
- https://rustsec.org/advisories/RUSTSEC-2026-0119.html
