Audit Report

## Title
Stale Cross-Chain Rate Served Without Staleness Guard Enables Over-Minting of rsETH at L2 Pools - (File: contracts/cross-chain/CrossChainRateReceiver.sol)

## Summary
`CrossChainRateReceiver.getRate()` unconditionally returns the last cached `rate` with no check against `lastUpdated`, meaning any L2 deposit pool (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPool`) will continue minting rsETH at an outdated exchange rate whenever the LayerZero cross-chain rate update is delayed. Because `updateRate()` on the provider side must be called explicitly and is not push-based on every L1 block, a staleness window between consecutive updates is a normal operating condition. Any depositor who observes a divergence between the L1 oracle price and the L2 cached rate can call `deposit()` to receive more rsETH than entitled, diluting the accrued yield of all existing holders.

## Finding Description

**Rate storage without staleness enforcement:**
`CrossChainRateReceiver` stores `rate` and `lastUpdated` as separate state variables. `lzReceive()` writes both on receipt, but `getRate()` returns `rate` unconditionally:

```solidity
// contracts/cross-chain/CrossChainRateReceiver.sol L95-104
rate = _rate;
lastUpdated = block.timestamp;
...
function getRate() external view returns (uint256) {
    return rate;  // no staleness check
}
```

`lastUpdated` is never read by any consumer in the codebase.

**Rate update is pull-based, not push-based:**
`MultiChainRateProvider.updateRate()` and `CrossChainRateProvider.updateRate()` must be called explicitly by an external caller. They are not triggered on every L1 block, so the staleness window between two consecutive updates is a normal operating condition, not an edge case.

**All L2 pools consume the rate through the same interface:**
`RSETHPoolV3.getRate()` → `IOracle(rsETHOracle).getRate()` → `CrossChainRateReceiver.getRate()`. The minting formula in `viewSwapRsETHAmountAndFee()` divides by the stale rate:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

The same pattern is present in `RSETHPoolV3ExternalBridge` and `RSETHPool`.

**Exploit flow:**
1. L1 `LRTOracle.rsETHPrice()` increases from `1.05e18` to `1.10e18` due to accumulated staking rewards.
2. The LayerZero `updateRate()` call has not yet been made; `CrossChainRateReceiver.rate` on the target L2 is still `1.05e18` and `lastUpdated` is hours old.
3. Attacker calls `RSETHPoolV3.deposit{value: 100 ether}("")`.
4. Pool computes `rsETHAmount = 100e18 * 1e18 / 1.05e18 ≈ 95.24 rsETH` instead of the correct `100e18 * 1e18 / 1.10e18 ≈ 90.91 rsETH`.
5. Attacker receives ≈4.33 rsETH more than entitled; total rsETH supply grows faster than underlying ETH, diluting every existing holder's redemption value.

**Existing checks are insufficient:**
The `paused` modifier and `dailyMintLimit` guard in `RSETHPoolV3` do not validate oracle freshness. No other check in any pool contract reads `lastUpdated` or enforces a maximum staleness window.

## Impact Explanation

**High — Theft of unclaimed yield.**

Each rsETH token represents a pro-rata claim on the underlying ETH. When new rsETH is minted at a stale lower rate, the total supply grows faster than the underlying ETH, diluting every existing holder's redemption value. The staking yield that existing holders had earned (the price appreciation from 1.05 to 1.10 ETH/rsETH) is effectively transferred to the depositor exploiting the staleness window. The magnitude scales with deposit size, the percentage divergence between stale and actual rate, and the duration of the staleness window. This matches the allowed impact: **High. Theft of unclaimed yield.**

## Likelihood Explanation

**Medium.** `updateRate()` must be called explicitly by any external caller; it is not automatic. The staleness window between two consecutive rate updates is a normal operating condition. A sophisticated depositor monitoring both the L1 `LRTOracle.rsETHPrice()` and the L2 `CrossChainRateReceiver.rate` can identify and exploit the divergence window without any privileged access — only a standard `deposit()` call is required. The attack is repeatable across every L2 chain that deploys an `RSETHRateReceiver` backed by a `CrossChainRateReceiver`.

## Recommendation

Add a configurable `maxStaleness` parameter to `CrossChainRateReceiver` and revert in `getRate()` if the cached rate is too old:

```solidity
uint256 public maxStaleness; // e.g., 24 hours

function getRate() external view returns (uint256) {
    require(
        lastUpdated != 0 && block.timestamp - lastUpdated <= maxStaleness,
        "Rate is stale"
    );
    return rate;
}
```

`maxStaleness` should be set conservatively (e.g., 24–48 hours) and be updatable by the owner. All L2 pool contracts inherit the protection automatically because they call `getRate()` through the `IOracle` interface.

## Proof of Concept

**Foundry fork test plan:**

1. Fork the target L2 at a block where `CrossChainRateReceiver.lastUpdated` is several hours old.
2. Confirm that `LRTOracle.rsETHPrice()` on L1 (via a separate fork or mock) is higher than `CrossChainRateReceiver.rate` on L2.
3. As an unprivileged address, call `RSETHPoolV3.deposit{value: 100 ether}("")`.
4. Record `rsETHMinted = wrsETH.balanceOf(attacker)`.
5. Assert `rsETHMinted > 100e18 * 1e18 / currentL1Rate` — i.e., the attacker received more rsETH than the correct L1 rate would entitle them to.
6. Compute the dilution to existing holders: `(rsETHMinted - correctAmount) / totalSupply * totalUnderlyingETH` represents the yield stolen from existing holders.

No privileged access is required; the only precondition is that `CrossChainRateReceiver.rate` has not been updated recently, which is a normal operating condition given the pull-based update mechanism.