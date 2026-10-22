# [H] Initialization of DyadXPv2 is impossible

## Summary
Severity: High
Contest weight: 0.5449
Dataset id: 7599
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
DyadXPv2.initialize() loops across the supply of DNFT:
```solidity
for (uint256 i = 0; i < dnftSupply; ++i) {
    noteData[i] = NoteXPData({
        lastAction: uint40(block.timestamp),
        keroseneDeposited: uint96(KEROSENE_VAULT.id2asset(i)),
        lastXP: noteData[i].lastXP,
        totalXP: noteData[i].lastXP,
        dyadMinted: DYAD.mintedDyad(i)
    });
}
```
The current total supply of DNFT is 882. gas used in 88 iterations is 3.130682e6 This means that the total cost of the loop is at least 3.130682e7, which exceeds the 3e7 (30M) gas limit.

## Recommendation
Consider not looping across the entire dnftSupply on initialization.
