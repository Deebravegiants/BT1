# [H] Bitcoin Inventory Out-of-Memory Denial-of-Service Attack (CVE-2018-17145)

## Summary
Severity: High
Advisory: GHSA-hx3r-jv9q-85jw
CVE: CVE-2018-17145
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-09-10
Source: https://github.com/advisories/GHSA-hx3r-jv9q-85jw
Type: github-advisory

## Affected
- npm: `bcoin` — affected >=0 <1.0.2

## Details
There was an easily exploitable uncontrolled memory resource consumption denial-of-service vulnerability that existed in the peer-to-peer network code of three implementations of Bitcoin and several alternative chains.

For more details please see:
https://invdos.net/

For the paper:
https://invdos.net/paper/CVE-2018-17145.pdf

## References
- https://github.com/bcoin-org/bcoin/security/advisories/GHSA-hx3r-jv9q-85jw
- https://nvd.nist.gov/vuln/detail/CVE-2018-17145
- https://en.bitcoin.it/wiki/Common_Vulnerabilities_and_Exposures#CVE-2018-17145
- https://github.com/bcoin-org/bcoin
- https://github.com/bitcoin/bitcoin/blob/v0.16.2/doc/release-notes.md
- https://invdos.net
- https://invdos.net/paper/CVE-2018-17145.pdf
