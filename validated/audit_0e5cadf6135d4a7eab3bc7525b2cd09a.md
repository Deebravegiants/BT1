Audit Report

## Title
Stale `rsETHPrice` in `instantWithdrawal` Allows Exit at Pre-Loss Rate, Transferring Losses to Remaining Holders - (File: `contracts/LRTWithdrawalManager.sol`)

## Summary

`LRTWithdrawalManager.instantWithdrawal` computes the asset payout using `LRTOracle.rsETHPrice`, a cached state variable updated only when `updateRSETHPrice()` is explicitly called. If a loss event (e.g., EigenLayer slashing) occurs before the oracle is refreshed, any rsETH holder can call `instantWithdrawal` at the stale pre-loss rate, receiving more assets than their proportional share. The resulting shortfall is silently absorbed by all remaining rsETH holders, constituting direct theft of their principal.

## Finding Description

`LRTOracle` stores the rsETH/ETH exchange rate in a state variable that is only written when `_updateRsETHPrice()` is invoked: [1](#0-0) [2](#0-1) 

`updateRSETHPrice()` is permissionless but is never called atomically by any withdrawal path. `getExpectedAssetAmount` reads this cached value directly: [3](#0-2) 

`instantWithdrawal` calls `getExpectedAssetAmount` at line 228 to determine the payout, then immediately burns rsETH and redeems from the unstaking vault — all without refreshing the oracle: [4](#0-3) 

The only guard present is a vault-balance check (`CantInstantWithdrawMoreThanAvailable`), which limits withdrawal to available vault liquidity but does not prevent payout at a stale, inflated price: [5](#0-4) 

By contrast, the queued withdrawal path applies `_calculatePayoutAmount`, which takes the **minimum** of the locked-in expected amount and the current return at unlock time, providing loss-sharing protection: [6](#0-5) 

The `pricePercentageLimit` downside-protection mechanism in `_updateRsETHPrice` only triggers a pause **after** the oracle is updated — it provides zero protection during the stale window: [7](#0-6) 

The `rsETHPrice` state variable is only written at the end of `_updateRsETHPrice`: [8](#0-7) 

## Impact Explanation

**Critical — Direct theft of principal funds from other rsETH holders.**

A user who exits via `instantWithdrawal` while `rsETHPrice` is stale receives assets valued at the inflated pre-loss rate. The shortfall is not immediately realized; it is absorbed by all remaining rsETH holders when `updateRSETHPrice()` is eventually called and the price drops. The PoC demonstrates that a 50% slashing event allows an attacker to withdraw 100% of their nominal ETH value, leaving remaining holders with worthless shares. This is direct theft of at-rest principal funds, matching the Critical impact class.

## Likelihood Explanation

Two conditions must hold simultaneously: (1) instant withdrawal must be enabled for the target asset (`isInstantWithdrawalEnabled[asset] == true`), which is a live protocol configuration for some assets; and (2) a loss event must have occurred but `updateRSETHPrice()` must not yet have been called. Condition 2 represents a realistic race window — `updateRSETHPrice()` is not called atomically with loss events, and a sophisticated user monitoring EigenLayer state can act within the same block or the next few blocks before any keeper refreshes the oracle. The attack is repeatable across any block in which the oracle is stale post-loss.

## Recommendation

Call `updateRSETHPrice()` (or an equivalent internal price refresh) at the start of `instantWithdrawal`, before computing `assetAmountUnlocked`:

```solidity
function instantWithdrawal(address asset, uint256 rsETHUnstaked, string calldata referralId)
    external nonReentrant whenNotPaused ...
{
    // Refresh oracle before computing payout
    ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE)).updateRSETHPrice();

    uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
    ...
}
```

Alternatively, enforce a maximum staleness window on `rsETHPrice` and revert if the price has not been updated within that window. A third option is to apply the same minimum-comparison guard used in `_calculatePayoutAmount` to the instant withdrawal path, capping the payout at the lesser of the stale-price amount and the live-price amount.

## Proof of Concept

1. Protocol has 200 ETH of staked assets backing 200 rsETH (`rsETHPrice = 1e18`). Instant withdrawal is enabled for ETH. The unstaking vault holds sufficient ETH for instant withdrawals.
2. EigenLayer slashing reduces the staked ETH to 100 ETH. `rsETHPrice` in `LRTOracle` remains `1e18` (stale) because `updateRSETHPrice()` has not been called.
3. BOB holds 100 rsETH. BOB calls `instantWithdrawal(ETH, 100e18, "")`.
4. `getExpectedAssetAmount` computes `100e18 * 1e18 / 1e18 = 100 ETH` using the stale price. The vault-balance check passes if the vault holds ≥ 100 ETH.
5. BOB's 100 rsETH is burned and he receives 100 ETH (minus fee) — the full pre-loss value.
6. ALICE holds the remaining 100 rsETH. When `updateRSETHPrice()` is eventually called, `_getTotalEthInProtocol()` reflects only the remaining 0 ETH (all withdrawn by BOB), and ALICE's shares are worthless.
7. BOB has extracted 100 ETH against a 50 ETH fair share, with the 50 ETH difference stolen from ALICE.

**Foundry fork test plan:** Deploy against a mainnet fork with instant withdrawal enabled. Simulate a slashing event by directly reducing the EigenLayer strategy balance (storage manipulation or mock). Confirm `rsETHPrice` is unchanged. Call `instantWithdrawal` as BOB. Assert BOB receives the pre-loss amount. Call `updateRSETHPrice()`. Assert ALICE's share value has dropped by the stolen amount.

### Citations

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
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

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTWithdrawalManager.sol (L228-235)
```text
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
        if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
            revert CantInstantWithdrawMoreThanAvailable();
        }

        unstakingVault.redeem(asset, assetAmountUnlocked);
```

**File:** contracts/LRTWithdrawalManager.sol (L590-593)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

**File:** contracts/LRTWithdrawalManager.sol (L833-834)
```text
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
```
