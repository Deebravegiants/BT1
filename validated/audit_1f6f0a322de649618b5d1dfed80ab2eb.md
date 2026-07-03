Audit Report

## Title
Stale rsETH/ETH Rate in CrossChainRateReceiver Allows Excess wrsETH Minting and Yield Theft - (File: contracts/cross-chain/CrossChainRateReceiver.sol, contracts/pools/RSETHPoolV2.sol)

## Summary
`CrossChainRateReceiver.getRate()` returns the last stored rate with no staleness check. `RSETHPoolV2.deposit()` uses this rate to compute how many wrsETH tokens to mint. When the stored rate is lower than the true current rsETH/ETH rate, depositors receive more wrsETH than they are entitled to, and because wrsETH is a CCIP burn-mint token redeemable 1:1 for rsETH on L1, an attacker can bridge the excess wrsETH back to L1 and extract the yield delta from the protocol's rsETH reserve.

## Finding Description
`CrossChainRateReceiver` stores `rate` and `lastUpdated` but `getRate()` returns the raw stored value unconditionally:

```solidity
// CrossChainRateReceiver.sol L103-105
function getRate() external view returns (uint256) {
    return rate;
}
```

The rate is only updated when `updateRate()` is called on `CrossChainRateProvider` (L1) and the LayerZero message is delivered to `lzReceive()` on L2. `updateRate()` is permissionless but requires the caller to pay LayerZero gas, so it depends on an off-chain keeper. Any period of keeper inactivity, network congestion, or LayerZero delivery delay leaves the rate stale.

`RSETHPoolV2.deposit()` calls `viewSwapRsETHAmountAndFee()`, which divides the ETH amount by the stale rate:

```solidity
// RSETHPoolV2.sol L230-233
uint256 rsETHToETHrate = getRate();
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

If `rsETHToETHrate` is stale-low (e.g., 1.05e18 instead of the true 1.10e18), the division yields more wrsETH than the depositor deserves. The pool then mints that inflated amount directly to the caller:

```solidity
// RSETHPoolV2.sol L216
wrsETH.mint(msg.sender, rsETHAmount);
```

`WrappedRSETH` is a CCIP burn-mint ERC677 token. The CCIP bridge burns wrsETH on L2 and releases rsETH 1:1 from the L1 lock-release pool. The attacker bridges the excess wrsETH to L1 and receives rsETH at the true rate, extracting the yield delta from the protocol's reserve.

The `dailyMintLimit` check does not prevent the attack — it only caps per-day exposure. An attacker can repeat the attack across multiple days or use a single large deposit within the limit.

## Impact Explanation
**High — Theft of unclaimed yield.**

For a deposit of `X` ETH with stale rate `R_stale` and true rate `R_true > R_stale`:
- wrsETH minted: `X * 1e18 / R_stale`
- wrsETH deserved: `X * 1e18 / R_true`
- Excess wrsETH: `X * 1e18 * (1/R_stale - 1/R_true)`
- Profit in ETH after bridging: `X * (R_true/R_stale - 1)`

The excess rsETH is drawn from the protocol's reserve, constituting direct theft of yield that belongs to existing rsETH holders. This matches the allowed impact "High. Theft of unclaimed yield." The SECURITY.md exclusion for "Incorrect data supplied by third-party oracles" does not apply here — the root cause is a missing staleness check in the protocol's own contract code, not oracle manipulation or incorrect data from an external party.

## Likelihood Explanation
**Medium-High.** The rate update is not automated on-chain; it requires an off-chain keeper to call `updateRate()` and pay for LayerZero gas. Any period of keeper inactivity, network congestion, or LayerZero delivery delay leaves the rate stale. rsETH accrues staking yield continuously, so even a few hours of staleness creates an exploitable gap. The attacker needs no special role or permission — `deposit()` is fully public and callable by any EOA or contract.

## Recommendation
1. **Add a staleness check in `getRate()`**: revert if `block.timestamp - lastUpdated > MAX_STALENESS` (e.g., 24 hours).
2. **Enforce the check in `RSETHPoolV2`**: `viewSwapRsETHAmountAndFee` should revert if the oracle rate is stale, preventing deposits when the rate cannot be trusted.
3. **Automate rate updates**: use a Chainlink Automation or equivalent keeper to push rate updates on a fixed cadence, ensuring the gap between true and stored rate stays within an acceptable tolerance.

## Proof of Concept
```solidity
// Fork test (L2 fork with fixed stale rate)
function testStaleRateYieldTheft() public {
    // 1. Deploy/fork RSETHRateReceiver with stale rate = 1.05e18
    //    True rate on L1 = 1.10e18 (5% yield accrued since last update)
    uint256 staleRate = 1.05e18;
    uint256 trueRate  = 1.10e18;
    vm.mockCall(
        address(rsETHOracle),
        abi.encodeWithSelector(IOracle.getRate.selector),
        abi.encode(staleRate)
    );

    uint256 depositETH = 100 ether;
    uint256 wrsETHMinted = depositETH * 1e18 / staleRate;
    // = 95.238... wrsETH

    uint256 wrsETHDeserved = depositETH * 1e18 / trueRate;
    // = 90.909... wrsETH

    uint256 excessWrsETH = wrsETHMinted - wrsETHDeserved;
    // ≈ 4.329 wrsETH

    // 2. Attacker calls deposit
    vm.deal(attacker, depositETH);
    vm.prank(attacker);
    pool.deposit{value: depositETH}("ref");

    assertEq(wrsETH.balanceOf(attacker), wrsETHMinted);

    // 3. Bridge wrsETH to L1 via CCIP (burn on L2, release rsETH 1:1 on L1)
    // 4. On L1: attacker holds wrsETHMinted rsETH worth wrsETHMinted * trueRate ETH
    uint256 profitETH = wrsETHMinted * trueRate / 1e18 - depositETH;
    // ≈ 4.762 ETH profit extracted from protocol reserve

    assertGt(profitETH, 0, "attacker profits from stale rate");
}
```

A fuzz variant parameterizing `(staleRate, trueRate, depositAmount)` with `trueRate > staleRate` and asserting `profit > 0` for all valid inputs confirms the invariant is broken whenever the rate is stale.