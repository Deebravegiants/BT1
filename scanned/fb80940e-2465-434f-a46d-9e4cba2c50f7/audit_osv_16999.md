# [H] CVE-2020-11071

## Summary
Severity: High
Advisory: CVE-2020-11071
Aliases: GHSA-jc83-cpf9-q7c6
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2020-05-12
Source: https://osv.dev/vulnerability/CVE-2020-11071
Type: osv

## Details
SLPJS (npm package slpjs) before version 0.27.2, has a vulnerability where users could experience false-negative validation outcomes for MINT transaction operations. A poorly implemented SLP wallet could allow spending of the affected tokens which would result in the destruction of a user's minting baton. This is fixed in version 0.27.2.

## References
- https://github.com/simpleledger/slpjs/security/advisories/GHSA-jc83-cpf9-q7c6
- https://github.com/simpleledger/slpjs/commit/3671be2ffb6d4cfa94c00c6dc8649d1ba1d75754
