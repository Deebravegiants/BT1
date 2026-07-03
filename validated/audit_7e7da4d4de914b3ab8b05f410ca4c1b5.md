Audit Report

## Title
Protocol Fee Charged on Gross Recovery After Loss Due to Missing High-Water Mark — (`contracts/LRTOracle.sol`)

## Summary

`_updateRsETHPrice()` computes `previousTVL` as `rsethSupply × rsETHPrice`, where `rsETHPrice` is the post-loss, post-fee stored price. After a TVL loss, `rsETHPrice` falls, lowering the fee baseline. On subsequent recovery, the protocol charges fees on the full gross recovery rather than only the net gain above the pre-loss fee-adjusted level. This causes the treasury to mint rsETH representing value that economically belongs to depositors, diluting all rsETH holders.

## Finding Description

In `_updateRsETHPrice()` at line 234, `previousTVL` is reconstructed each call as:

```solidity
uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);
```

`rsETHPrice` (line 313) is overwritten at the end of every update with the new post-fee price. When a loss occurs (`totalETHInProtocol < previousTVL`), no fee is charged and `rsETHPrice` is written to the lower post-loss value. This lowers `previousTVL` for the next call. When TVL recovers, the condition at line 244 (`totalETHInProtocol > previousTVL`) becomes true against this artificially lowered baseline, and the fee at line 246 is charged on the entire gross recovery — including the portion that merely restores previously lost principal.

The contract does store `highestRsethPrice` (line 30), but it is used exclusively for the price-change percentage guard (lines 252–291) and is never consulted in the fee computation path. There is no high-water mark for fee purposes.

Concrete PoC trace (10% fee rate):

| Step | `totalETHInProtocol` | `rsETHPrice` stored | `previousTVL` | Fee charged |
|------|---------------------|---------------------|---------------|-------------|
| 1 | 1000 | 1.000 | — | — |
| 2 | 1100 | 1.090 | 1000 | 10 ETH (correct) |
| 3 | 1020 | 1.020 | 1090 | 0 (loss) |
| 4 | 1100 | 1.092 | 1020 | **8 ETH** (should be 1 ETH) |

Net gain since last fee-bearing update: 10 ETH → correct fee = 1 ETH. Actual fee = 8 ETH. Treasury extracts 7 ETH of depositor principal recovery.

## Impact Explanation

**High — Theft of unclaimed yield.** The treasury mints rsETH backed by ETH that represents a recovery of depositor principal, not new yield. Every rsETH holder is diluted proportionally. The magnitude scales with `(lossAmount × protocolFeeInBPS / 10_000)` and is repeatable across every loss-recovery cycle. This directly matches the allowed impact "Theft of unclaimed yield."

## Likelihood Explanation

`updateRSETHPrice()` is public with no access control (line 87). Any address can call it. EigenLayer restaking strategies are subject to slashing and market fluctuations, making partial loss-recovery cycles realistic and recurring. No privileged actor, governance action, or victim mistake is required — any external caller invoking `updateRSETHPrice()` after a loss-recovery cycle triggers the over-fee.

## Recommendation

Introduce a `feeHighWaterMarkTVL` storage variable that is set to `totalETHInProtocol` after each fee-bearing update and is **never decreased** on losses. Replace line 234's `previousTVL` with this high-water mark for the fee comparison and fee base calculation. The existing `rsETHPrice` can continue to reflect the true current price (including losses) for all other purposes. Alternatively, track `feeHighWaterMarkTVL` as `rsethSupply × highestRsethPrice` (already stored), since `highestRsethPrice` is never reduced — but only if `highestRsethPrice` is updated after each fee deduction to reflect the post-fee price.

## Proof of Concept

Foundry unit test plan:

1. Deploy `LRTOracle` with a mock `LRTConfig` returning `protocolFeeInBPS = 1000` (10%).
2. Set `rsETHPrice = 1e18`, `rsethSupply = 1000e18`, mock `_getTotalEthInProtocol` returning `1100e18`. Call `updateRSETHPrice()`. Record treasury rsETH balance B1.
3. Mock `_getTotalEthInProtocol` returning `1020e18`. Call `updateRSETHPrice()`. Verify no fee minted.
4. Mock `_getTotalEthInProtocol` returning `1100e18`. Call `updateRSETHPrice()`. Record treasury rsETH balance B2.
5. Assert `B2 - B1 ≈ 1e18 / newRsETHPrice` (≈1 ETH worth of rsETH). The actual result will be `≈8 ETH` worth, proving the overcharge. Fuzz the loss magnitude to show the overcharge scales linearly with loss size.