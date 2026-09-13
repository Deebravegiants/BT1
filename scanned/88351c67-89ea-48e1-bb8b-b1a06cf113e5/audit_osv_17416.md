# [H] CVE-2020-15130

## Summary
Severity: High
Advisory: CVE-2020-15130
Aliases: GHSA-cc2p-4jhr-xhhx
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-07-30
Source: https://osv.dev/vulnerability/CVE-2020-15130
Type: osv

## Details
In SLPJS (npm package slpjs) before version 0.27.4, there is a vulnerability to false-positive validation outcomes for the NFT1 Child Genesis transaction type. A poorly implemented SLP wallet or opportunistic attacker could create a seemingly valid NFT1 child token without burning any of the NFT1 Group token type as is required by the NFT1 specification. This is fixed in version 0.27.4.

## References
- https://github.com/simpleledger/slpjs/security/advisories/GHSA-cc2p-4jhr-xhhx
- https://github.com/simpleledger/slpjs/commit/290c20e8bff13ac81459d43e54cac232b5e3456c
