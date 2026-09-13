# [H] CVE-2020-11014

## Summary
Severity: High
Advisory: CVE-2020-11014
Aliases: GHSA-cchm-grx2-g873
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2020-04-28
Source: https://osv.dev/vulnerability/CVE-2020-11014
Type: osv

## Details
Electron-Cash-SLP before version 3.6.2 has a vulnerability. All token creators that use the "Mint Tool" feature of the Electron Cash SLP Edition are at risk of sending the minting authority baton to the wrong SLP address. Sending the mint baton to the wrong address will give another party the ability to issue new tokens or permanently destroy future minting capability. This is fixed version 3.6.2.

## References
- https://github.com/kristovatlas/rfc/blob/master/bips/bip-li01.mediawiki
- https://github.com/simpleledger/Electron-Cash-SLP/issues/126
- https://github.com/simpleledger/Electron-Cash-SLP/security/advisories/GHSA-cchm-grx2-g873
- https://github.com/simpleledger/Electron-Cash-SLP/commit/ea3912c3d508ba81b280ef7d78648464f7f76fb8
