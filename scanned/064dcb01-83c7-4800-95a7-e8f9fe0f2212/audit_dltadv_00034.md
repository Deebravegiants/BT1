# [M] Consensus failures in github.com/btcsuite/btcd

## Summary
Severity: Medium
Advisory: GO-2024-2818
Aliases: CVE-2024-34478, GHSA-3jgf-r68h-xfqm
Package: github.com/btcsuite/btcd
Published: 2024-05-08
Source: https://osv.dev/vulnerability/GO-2024-2818
Type: chain-advisory

## Affected
- Go: `github.com/btcsuite/btcd` — affected >=0 <0.24.0

## Details
Incorrect implementation of the consensus rules outlined in BIP 68 and BIP 112 making btcd susceptible to consensus failures. Specifically, it uses the transaction version as a signed integer when it is supposed to be treated as unsigned. There can be a chain split and loss of funds.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-34478
- https://delvingbitcoin.org/t/disclosure-btcd-consensus-bugs-due-to-usage-of-signed-transaction-version/455
- https://github.com/btcsuite/btcd/blob/e4c88c3a3ecb1813529bf3dddc7a865bd418a6b8/blockchain/chain.go#L383C1-L392C3
- https://github.com/btcsuite/btcd/blob/e4c88c3a3ecb1813529bf3dddc7a865bd418a6b8/txscript/opcode.go#L1172C1-L1178C3
- https://github.com/btcsuite/btcd/pull/1981
