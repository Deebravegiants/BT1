# [H] BER/CER/DER decoder panics on invalid input

## Summary
Severity: High
Advisory: GHSA-6jmw-6mxw-w4jc
CVE: CVE-2023-39914
CWE: CWE-228, CWE-232
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-09-13
Source: https://github.com/advisories/GHSA-6jmw-6mxw-w4jc
Type: github-advisory

## Affected
- crates.io: `bcder` — affected >=0 <0.7.3

## Details
NLnet Labs’ bcder library up to and including version 0.7.2 panics while decoding certain invalid input data rather than rejecting the data with an error. This can affect both the actual decoding stage as well as accessing content of types that utilized delayed decoding.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39914
- https://github.com/NLnetLabs/bcder/commit/4da91c3fd853e3d466d8581cf1d82b7f3255de56
- https://github.com/NLnetLabs/bcder
- https://nlnetlabs.nl/downloads/bcder/CVE-2023-39914.txt
- https://rustsec.org/advisories/RUSTSEC-2023-0062.html
