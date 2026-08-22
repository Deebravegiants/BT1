# [M] No check if get_D actually converges

## Summary
Severity: Medium
Chain: Smart contract
Component: Thorn-protocol
Published: 2024-10-03
Source: https://github.com/hats-finance/Thorn-protocol-0x1286ecdac50215a366458a14968fbca4bd95067d/issues/52
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x739fe19b2a92509639349db8e28b0da7d3daac96f4090c5114690d5c8571f148
**Severity:** medium

**Description:**
**Description**\
The [get_D function](https://github.com/hats-finance/Thorn-protocol-0x1286ecdac50215a366458a14968fbca4bd95067d/blob/main/contracts/stableSwap/plain-pools/StableSwapTwoPool.sol#L233) doesn't check if when calculating the invariant the Newton's method used for that converges. In case it doesn't, the pool will be broken because of an inaccurate invariant. 

You can reference an updated implementation from Curve's team here: https://github.com/curvefi/stableswap-ng/blob/main/contracts/main/CurveStableSwapNG.vy#L1123
**Attack Scenario**\
While it's rare that the Newton's method doesn't converge and in the stableswap formula it usually does in 4 steps, in the rare case that it doesn't, the pool's invariant will be broken and won't be accurately updated, which can lead to loss of funds for the pool(and the LPs in the pool).
**Attachments**

1. **Proof of Concept (PoC) File**
```solidity
function get_D(uint256[N_COINS] memory xp, uint256 amp) internal pure returns (uint256) {
        uint256 S;
        for (uint256 i = 0; i < N_COINS; i++) {
            S += xp[i];
        }
        if (S == 0) {
            return 0;
        }

        uint256 Dprev;
        uint256 D = S;
        uint256 Ann = amp * N_COINS;
        for (uint256 j = 0; j < 255; j++) {
            uint256 D_P = D;
            for (uint256 k = 0; k < N_COINS; k++) {
                D_P = (D_P * D) / (xp[k] * N_COINS); // If division by 0, this will be borked: only withdrawal will work. And that is good
            }
            Dprev = D;
            D = ((Ann * S + D_P * N_COINS) * D) / ((Ann - 1) * D + (N_COINS + 1) * D_P);
            // Equality with the precision of 1
            if (D > Dprev) {
                if (D - Dprev <= 1) {
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Thorn-protocol-0x1286ecdac50215a366458a14968fbca4bd95067d/issues/52_
