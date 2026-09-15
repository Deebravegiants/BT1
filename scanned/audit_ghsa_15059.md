# [H] SPV Merkle proof malleability allows the maintainer to prove invalid transactions

## Summary
Severity: High
Advisory: GHSA-wg2x-rv86-mmpx
Ecosystem: npm
Published: 2024-01-19
Source: https://github.com/advisories/GHSA-wg2x-rv86-mmpx
Type: github-advisory

## Affected
- npm: `@keep-network/tbtc-v2` — affected >=0 <1.5.2

## Details
## Summary
By publishing specially crafted transactions on the Bitcoin blockchain, the SPV maintainer can produce seemingly valid SPV proofs for fraudulent transactions.

The issue was originally identified by Least Authority in the tBTC Bridge V2 Security Audit Report as _Issue B: Bitcoin SPV Merkle Proofs Can Be Faked_. A mitigation was believed to have been in place, but this turned out to contain an error, and the issue had not been effectively mitigated.

### Details
This is achieved by creating a 64-byte transaction that the fraudulent transaction treats as a node in its merkle proof:

The attacker creates the malicious transaction `E` and calculates an unusual but valid transaction `D`, so that the last 32 bytes of `D` are a part of the merkle proof of `E`:

```
D = foo | hash256(E')
E' = bar | hash256(E)
```

`foo` and `bar` are arbitrary 32-byte values selected to facilitate this attack.

The attacker can then publish `D` and wait for it to be mined. A valid SPV proof for `D` can then be transformed into a proof for `E` by prepending `bar` and `foo` to the merkle proof, and changing the transaction index into one matching `E`'s implied position in the merkle tree.

Calculating a suitable value for `E'` has been estimated to require between 2\^60 to 2\^81 operations. By contrast, the current Bitcoin hashrate is approximately 2\^69. Thus the cost of performing the requisite brute-force is at most similar to, or possibly up to 1,000,000 times lower than, the cost of mining 6 Bitcoin blocks at the current difficulty.

### Impact
The vulnerability does not enable the SPV maintainer to do anything they would not have been able to do otherwise. However, the ability to bypass the need to mine 6 blocks at the current difficulty makes abusing the SPV maintainer position significantly cheaper.

### Patches
Adding the coinbase transaction and its merkle proof into the SPV proofs prevents this issue, by increasing the brute-force required to 2\^224. If the length of the coinbase proof matches the length of the transaction proof, and both proofs are valid for the same header, we can trust that the exploit has not been abused for the transaction.

### Workarounds
The trusted SPV maintainer position prevents this issue

### References
[Weaknesses in Bitcoin’s Merkle Root Construction](https://lists.linuxfoundation.org/pipermail/bitcoin-dev/attachments/20190225/a27d8837/attachment-0001.pdf)

[Leaf-Node weakness in Bitcoin Merkle Tree Design](https://bitslog.com/2018/06/09/leaf-node-weakness-in-bitcoin-merkle-tree-design/)

[SPV proof verification vulnerable to potential (but expensive to exploit) Merkle tree problem \#192](https://github.com/summa-tx/bitcoin-spv/issues/192)

[tBTC Bridge V2 Security Audit Report](https://leastauthority.com/static/publications/LeastAuthority_KeepNetwork_tBTC_Bridge_v2_Updated_Final_Audit_Report.pdf)

## References
- https://github.com/keep-network/tbtc-v2/security/advisories/GHSA-wg2x-rv86-mmpx
- https://github.com/summa-tx/bitcoin-spv/issues/192
- https://github.com/keep-network/tbtc-v2/commit/20a6fb1bfb23d4a3d5b90e00eaa7cc2abc9a2871
- https://bitslog.com/2018/06/09/leaf-node-weakness-in-bitcoin-merkle-tree-design
- https://github.com/keep-network/tbtc-v2
- https://leastauthority.com/static/publications/LeastAuthority_KeepNetwork_tBTC_Bridge_v2_Updated_Final_Audit_Report.pdf
- https://lists.linuxfoundation.org/pipermail/bitcoin-dev/attachments/20190225/a27d8837/attachment-0001.pdf
