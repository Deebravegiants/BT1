### Title
Stale `rsETHPrice` Allows `instantWithdrawal` Users to Extract More Assets Than Their Fair Share Before Loss Is Reflected — (File: `contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager.instantWithdrawal` computes the asset payout using the stored, potentially stale `LRTOracle.rsETHPrice`. Unlike the queued-withdrawal path (`unlockQueue` → `_calculatePayoutAmount`), which applies a `min(expectedAssetAmount, currentReturn)` cap at unlock time, `instantWithdrawal` has no such protection. When EigenLayer slashing reduces protocol TVL but `updateRSETHPrice()` has not yet been called, any user can call `instantWithdrawal` at the pre-loss price, extracting more assets than their proportional share and shifting the entire loss onto remaining rsETH holders.

---

### Finding Description

`LRTOracle.rsETHPrice` is a stored value updated only when `updateRSETHPrice()` is explicitly called: [1](#0-0) 

Between a slashing event and the next `updateRSETHPrice()` call, `rsETHPrice` remains at its pre-loss value. `getExpectedAssetAmount` in `LRTWithdrawalManager` reads this stale value directly: [2](#0-1) 

In `instantWithdrawal`, the payout is computed from this stale price and immediately transferred to the user with no correction: [3](#0-2) 

The only guard is a vault-balance check, which does not prevent over-payment relative to fair share: [4](#0-3) 

By contrast, the queued-withdrawal path in `_calculatePayoutAmount` applies `min(expectedAssetAmount, currentReturn)` at unlock time, which correctly absorbs any price drop: [5](#0-4) 

`instantWithdrawal` has no equivalent protection.

---

### Impact Explanation

**Critical — Direct theft of user funds.**

A user who calls `instantWithdrawal` while `rsETHPrice` is stale (higher than the post-loss fair value) burns the correct amount of rsETH but receives more underlying assets than their proportional share. The deficit is silently absorbed by all remaining rsETH holders, whose shares now back fewer real assets. This is a direct, quantifiable transfer of value from passive holders to the withdrawing user.

Example:
- Protocol TVL: 300 ETH, rsETH supply: 300, price = 1 ETH/rsETH
- EigenLayer slashing removes 30 ETH → true price = 0.9 ETH/rsETH
- `updateRSETHPrice()` not yet called; `rsETHPrice` still = 1 ETH
- Bob calls `instantWithdrawal` with 100 rsETH → receives 100 ETH (stale price)
- After price update: remaining 200 rsETH backs only 170 ETH → price = 0.85 ETH/rsETH
- Alice and Chris bear Bob's 10 ETH excess extraction on top of the original 30 ETH loss

---

### Likelihood Explanation

**High.**

EigenLayer slashing is an explicitly acknowledged risk in the protocol (the `LRTOracle` downside-protection pause mechanism exists precisely for this). `updateRSETHPrice()` is not called atomically with slashing; there is always a window. `instantWithdrawal` is a permissionless, publicly callable function (when enabled per asset). Any rsETH holder monitoring on-chain events can detect a slashing before the oracle is updated and exploit this window.

---

### Recommendation

Apply the same `min(expectedAssetAmount, currentReturn)` cap used in `_calculatePayoutAmount` inside `instantWithdrawal`. Specifically, compute the current fair return at execution time using the live oracle prices and cap the payout:

```solidity
uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
// Cap to current fair value to prevent stale-price over-extraction
uint256 currentFairAmount = (rsETHUnstaked * lrtOracle.rsETHPrice()) / lrtOracle.getAssetPrice(asset);
assetAmountUnlocked = assetAmountUnlocked < currentFairAmount ? assetAmountUnlocked : currentFairAmount;
```

Alternatively, call `updateRSETHPrice()` atomically at the start of `instantWithdrawal` to ensure the price is always fresh before computing the payout.

---

### Proof of Concept

1. Protocol state: 300 ETH TVL, 300 rsETH supply, `rsETHPrice = 1e18`, `isInstantWithdrawalEnabled[ETH] = true`, `LRTUnstakingVault` holds 100 ETH.
2. EigenLayer slashing event reduces protocol ETH by 30 ETH (true TVL = 270 ETH). `updateRSETHPrice()` has not been called yet; `rsETHPrice` remains `1e18`.
3. Bob holds 100 rsETH. Bob calls `instantWithdrawal(ETH_TOKEN, 100e18, "")`.
4. `getExpectedAssetAmount` computes `100e18 * 1e18 / 1e18 = 100e18` (100 ETH) using stale price.
5. Vault balance check passes (vault has 100 ETH).
6. Bob's 100 rsETH is burned; Bob receives 100 ETH.
7. `updateRSETHPrice()` is now called: TVL = 170 ETH (270 - 100 paid to Bob), supply = 200 rsETH → new price = 0.85 ETH/rsETH.
8. Alice and Chris each hold 100 rsETH now worth only 85 ETH instead of the 90 ETH they would have had if Bob had withdrawn at the fair post-loss price of 0.9 ETH/rsETH. Bob extracted 10 ETH in excess of his fair share, entirely at Alice and Chris's expense. [6](#0-5) [1](#0-0) [7](#0-6)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTWithdrawalManager.sol (L212-253)
```text
    function instantWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
        onlyInstantWithdrawalAllowed(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }
        if (IERC20(lrtConfig.rsETH()).balanceOf(msg.sender) < rsETHUnstaked) revert NotEnoughRsETH();
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
        if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
            revert CantInstantWithdrawMoreThanAvailable();
        }

        unstakingVault.redeem(asset, assetAmountUnlocked);

        uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;
        uint256 userAmount = assetAmountUnlocked - fee;

        address feeRecipient = instantWithdrawalFeeRecipient;
        if (feeRecipient == address(0)) {
            // Backwards-compatible default: send fees to the protocol treasury
            feeRecipient = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        }
        if (fee > 0) {
            _transferAsset(asset, feeRecipient, fee);
            emit InstantWithdrawalFeeCollected(msg.sender, asset, fee);
        }

        _transferAsset(asset, msg.sender, userAmount);
        emit ReferralIdEmitted(referralId);
        emit AssetWithdrawalFinalized(msg.sender, asset, rsETHUnstaked, userAmount);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L580-594)
```text
    function getExpectedAssetAmount(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 underlyingToReceive)
    {
        // setup oracle contract
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L833-834)
```text
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
```
