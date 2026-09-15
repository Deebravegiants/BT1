# [H] btcd did not correctly re-implement Bitcoin Core's "FindAndDelete()" functionality

## Summary
Severity: High
Advisory: GHSA-27vh-h6mc-q6g8
CVE: CVE-2024-38365
CWE: CWE-670
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2024-10-10
Source: https://github.com/advisories/GHSA-27vh-h6mc-q6g8
Type: github-advisory

## Affected
- Go: `github.com/btcsuite/btcd` — affected >=0 <0.24.2-beta.rc1

## Details
### Impact

The btcd Bitcoin client (versions 0.10 to 0.24) did not correctly re-implement Bitcoin Core's "FindAndDelete()" functionality. This
logic is consensus-critical: the difference in behavior with the other Bitcoin clients can lead to btcd clients accepting an invalid Bitcoin block (or rejecting a valid one). 

This consensus failure can be leveraged to cause a chain split (accepting an invalid Bitcoin block) or be exploited to DoS the btcd nodes (rejecting a valid Bitcoin block). An attacker can create a standard transaction where FindAndDelete doesn't return a match but removeOpCodeByData does making btcd get a different sighash, leading to a chain split. Importantly, this vulnerability can be exploited remotely by any Bitcoin user and does not require any hash power. This is because the difference in behavior can be triggered by a "standard" Bitcoin
transaction, that is a transaction which gets relayed through the P2P network before it gets included in a Bitcoin block.

#### `FindAndDelete` vs. `removeOpcodeByData`

`removeOpcodeByData(script []byte, dataToRemove []byte)` removes any data pushes from `script` that *contain* `dataToRemove`. However, `FindAndDelete` only removes *exact* matches. So for example, with `script = "<data> <data||foo>"` and `dataToRemove = "data"` btcd will remove both data pushes but Bitcoin Core's `FindAndDelete` only removes the first `<data>` push.


### Patches

This has been patched in `btcd` version v0.24.2-beta. 

### References

`FindAndDelete`: https://github.com/btcsuite/btcd/security/advisories/GHSA-27vh-h6mc-q6g8

## References
- https://github.com/btcsuite/btcd/security/advisories/GHSA-27vh-h6mc-q6g8
- https://nvd.nist.gov/vuln/detail/CVE-2024-38365
- https://github.com/btcsuite/btcd/commit/04469e600e7d4a58881e2e5447d19024e49800f5
- https://delvingbitcoin.org/t/cve-2024-38365-public-disclosure-btcd-findanddelete-bug/1184
- https://github.com/btcsuite/btcd
- https://github.com/btcsuite/btcd/releases/tag/v0.24.2
