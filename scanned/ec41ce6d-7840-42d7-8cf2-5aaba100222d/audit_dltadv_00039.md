# [H] Consensus failure in github.com/btcsuite/btcd

## Summary
Severity: High
Advisory: GO-2024-3189
Aliases: CVE-2024-38365, GHSA-27vh-h6mc-q6g8
Package: github.com/btcsuite/btcd
Published: 2024-10-15
Source: https://osv.dev/vulnerability/GO-2024-3189
Type: chain-advisory

## Affected
- Go: `github.com/btcsuite/btcd` — affected >=0 <0.24.2-beta.rc1

## Details
The btcd Bitcoin client (versions 0.10 to 0.24) did not correctly re-implement Bitcoin Core's 'FindAndDelete()' functionality, causing discrepancies in the validation of Bitcoin blocks. This can lead to a chain split (accepting an invalid block) or Denial of Service (DoS) attacks (rejecting a valid block). An attacker can trigger this vulnerability by constructing a 'standard' Bitcoin transaction that exhibits different behaviors in 'FindAndDelete()' and 'removeOpcodeByData()'.

## References
- https://github.com/btcsuite/btcd/security/advisories/GHSA-27vh-h6mc-q6g8
- https://github.com/btcsuite/btcd/commit/04469e600e7d4a58881e2e5447d19024e49800f5
- https://delvingbitcoin.org/t/cve-2024-38365-public-disclosure-btcd-findanddelete-bug/1184
- https://github.com/btcsuite/btcd/releases/tag/v0.24.2
