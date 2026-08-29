# [H] `FM_Rebasing_v1` is vounerable to just in time liquidity

## Summary
Severity: High
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-15
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/128
Type: hats-finding

## Details
**Github username:** @0x3b33
**Twitter username:** @0x3b33
**Submission hash (on-chain):** 0xa97510eedf2caa18cca5455d3d7b08bc891c5e470687ef5c1f2069f60f6da1ed
**Severity:** high

**Description:**
**Description**\
[FM_Rebasing_v1](https://github.com/InverterNetwork/audit-hats/blob/09e3a91bdc298a8666f666efbce408178cd83ec8/src/modules/fundingManager/rebasing/FM_Rebasing_v1.sol) is vulnerable to JIT (just in time liquidity). Users can front-run an increase in bit value and deposit large amounts of assets. The same can be said for withdrawals, where users will avoid a value decrease.

**Attack Scenario**\
A user can track deposit TX (not normal ones, but ones that increase the bits value) front-run them by making a large deposit, and then back-run them with a withdrawal. This allows them to extract a portion of the rewards with no risk.

Example:
- There are 5k tokens in the rebasing vault.
- The bit : token ratio is 10 (a small number to simplify the math).

1. The protocol makes a small profit and sends 1000 tokens to the vault (20%).
2. Bob sees the transaction and front-runs it with a deposit of 5000 tokens (now owning 50% of the pool).
3. After the 1000 token increase the new bit ratio will be 11 (as 1000 is 10% of 10k).
4. Bob withdraws his bits, claiming 50% of the tokens - 11k * 50% = 5500.

Bob profited 50% of the rewards that should have been sent to active depositors. In real scenarios, the profits might not be that large, however, some parts of the value increase will still be MEV'd.

**Recommendation**\
Implement a withdrawal window to disincentivize whales from sandwiching value increases.
