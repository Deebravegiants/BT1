### Title
`_updateRsETHPrice` Silently Discards Protocol TVL When `rsethSupply == 0`, Enabling Theft of Accrued Yield — (`contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle._updateRsETHPrice()` contains an early-return branch that fires when `rsethSupply == 0`. It unconditionally resets both `rsETHPrice` and `highestRsethPrice` to `1 ether` and returns without ever reading `_getTotalEthInProtocol()`. Any ETH that remains in the protocol at that moment — staking rewards still in EigenLayer pods, ETH mid-unstaking, or residual balances in `LRTUnstakingVault` — is silently orphaned. The first depositor after the reset captures that ETH for free, constituting theft of unclaimed yield.

---

### Finding Description

`_updateRsETHPrice()` in `LRTOracle.sol` handles the zero-supply case as follows:

```solidity
uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

if (rsethSupply == 0) {
    rsETHPrice = 1 ether;
    highestRsethPrice = 1 ether;
    return;                        // ← never reads totalETHInProtocol
}
``` [1](#0-0) 

The function returns before calling `_getTotalEthInProtocol()`, which aggregates ETH across `LRTDepositPool`, all `NodeDelegator` contracts, EigenLayer pod shares, `LRTUnstakingVault`, and `LRTConverter`:

```solidity
uint256 totalETHInProtocol = _getTotalEthInProtocol();
``` [2](#0-1) 

`_getTotalEthInProtocol()` itself sums `getEffectivePodShares()` and `getAssetUnstaking()` from every NodeDelegator, meaning ETH that is mid-unstake from EigenLayer (subject to the EigenLayer withdrawal delay) is still counted as protocol TVL: [3](#0-2) 

When `rsethSupply` reaches zero — which happens after `unlockQueue()` burns the last rsETH — any ETH still in-flight through EigenLayer's withdrawal queue is not yet redeemable by users, yet it is real protocol value. The zero-supply branch ignores it entirely and resets the price anchor to `1 ether`.

A second consequence is that `highestRsethPrice` is also reset to `1 ether`. This variable is the reference for the downside-protection circuit-breaker:

```solidity
if (newRsETHPrice < highestRsethPrice) {
    bool isPriceDecreaseOffLimit =
        pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);
    if (isPriceDecreaseOffLimit) { ... _pause(); return; }
}
``` [4](#0-3) 

Resetting `highestRsethPrice` to `1 ether` when the true all-time-high was, say, `1.1 ether` means the circuit-breaker's reference is permanently lowered, weakening downside protection for the next cycle.

---

### Impact Explanation

**Theft of unclaimed yield.** After all rsETH is burned and the price is reset to `1 ether`, any ETH that remains in the protocol (EigenLayer pod rewards, mid-unstake ETH, residual balances) is not reflected in the price. The first depositor mints rsETH at `1 ether` per token. On the next `updateRSETHPrice()` call, `_getTotalEthInProtocol()` returns the orphaned ETH plus the new deposit, so `rsETHPrice` jumps above `1 ether`. The first depositor can immediately withdraw at the higher price, capturing the yield that belonged to the previous rsETH holders.

**Downside-protection weakening.** `highestRsethPrice` is reset to `1 ether`, so the circuit-breaker that pauses the protocol on large price drops uses a lower reference than the true historical peak, allowing a larger absolute price drop before the pause triggers.

---

### Likelihood Explanation

`rsethSupply` reaching zero requires all outstanding rsETH to be burned. This occurs naturally when every user completes the withdrawal lifecycle (`initiateWithdrawal` → `unlockQueue` → `completeWithdrawal`). EigenLayer's mandatory withdrawal delay (currently ~7 days) means ETH is routinely in-flight during this window. The public `updateRSETHPrice()` function can be called by anyone while the protocol is unpaused, so an attacker only needs to monitor for the zero-supply condition and act first. [5](#0-4) 

---

### Recommendation

Before returning early in the zero-supply branch, check whether `_getTotalEthInProtocol()` is non-zero. If it is, either:

1. Revert (preventing the price reset until the orphaned ETH is accounted for), or
2. Preserve `rsETHPrice` and `highestRsethPrice` at their last non-zero values rather than resetting them to `1 ether`.

Do **not** reset `highestRsethPrice` to `1 ether` unconditionally; preserve the historical peak so the circuit-breaker reference is not weakened on protocol restart.

---

### Proof of Concept

1. Protocol runs normally; `rsETHPrice = 1.1 ether`, `highestRsethPrice = 1.1 ether`.
2. All users call `initiateWithdrawal(ETH, ...)`. rsETH is held in `LRTWithdrawalManager`.
3. Operator calls `unlockQueue(ETH, ...)`. All rsETH is burned via `IRSETH.burnFrom`. `rsethSupply = 0`. EigenLayer withdrawal delay means ~0.05 ETH of staking rewards is still in-flight inside `getEffectivePodShares()`.
4. Anyone calls `updateRSETHPrice()`. The zero-supply branch fires: `rsETHPrice = 1 ether`, `highestRsethPrice = 1 ether`. The 0.05 ETH is never read.
5. Attacker calls `LRTDepositPool.depositETH{value: 1 ether}(0, "")`. `getRsETHAmountToMint` computes `1e18 * 1e18 / 1e18 = 1e18` rsETH minted at `rsETHPrice = 1 ether`.
6. EigenLayer withdrawal completes; 0.05 ETH lands in `LRTUnstakingVault` / `LRTDepositPool`. `_getTotalEthInProtocol()` now returns `1.05 ether`.
7. Anyone calls `updateRSETHPrice()`. `newRsETHPrice = 1.05e18 / 1e18 = 1.05 ether`.
8. Attacker calls `initiateWithdrawal` + `unlockQueue` + `completeWithdrawal`, receiving `1.05 ETH` for their `1 rsETH`. Net gain: `0.05 ETH` of yield that belonged to the previous depositors. [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L216-222)
```text
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }
```

**File:** contracts/LRTOracle.sol (L231-231)
```text
        uint256 totalETHInProtocol = _getTotalEthInProtocol();
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L270-282)
```text
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
```

**File:** contracts/LRTDepositPool.sol (L484-493)
```text
        for (uint256 i; i < ndcsCount;) {
            ethLyingInNDCs += nodeDelegatorQueue[i].balance;

            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
            unchecked {
                ++i;
            }
        }
```

**File:** contracts/LRTDepositPool.sol (L506-521)
```text
    function getRsETHAmountToMint(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 rsethAmountToMint)
    {
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
