### Title
`instantWithdrawal` uses stale `rsETHPrice` to compute payout, allowing users to exit at pre-slash rate and shift losses to remaining rsETH holders - (File: `contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager.instantWithdrawal()` computes the asset payout using the stored `rsETHPrice` from `LRTOracle` without first calling `updateRSETHPrice()`. When an EigenLayer slash reduces the protocol's total ETH, the stored price becomes stale. Any user who calls `instantWithdrawal()` before the price is refreshed receives more assets than their rsETH is currently worth, effectively offloading the slash loss onto remaining rsETH holders.

---

### Finding Description

`LRTOracle.rsETHPrice` is a stored value updated only when `updateRSETHPrice()` is explicitly called — it is not refreshed atomically with EigenLayer slashing events. The `instantWithdrawal()` function computes the payout via `getExpectedAssetAmount(asset, rsETHUnstaked)`, which resolves to:

```
assetAmountUnlocked = (rsETHUnstaked × rsETHPrice) / assetPrice
```

using the stored (potentially stale) `lrtOracle.rsETHPrice()`. [1](#0-0) 

There is no call to `updateRSETHPrice()` inside `instantWithdrawal()` before this calculation. The price is only updated when someone separately calls `LRTOracle.updateRSETHPrice()`, which is a standalone public transaction. [2](#0-1) 

The `_updateRsETHPrice()` internal function recomputes the price from `_getTotalEthInProtocol()`, which sums `getEffectivePodShares()` across all `NodeDelegator` contracts. A slash in EigenLayer reduces these shares, lowering `totalETHInProtocol` and thus the true rsETH price — but this is only reflected in `rsETHPrice` after an explicit `updateRSETHPrice()` call. [3](#0-2) 

By contrast, the queued `initiateWithdrawal` path is partially protected: `_calculatePayoutAmount` takes the **minimum** of the locked `expectedAssetAmount` and the current return at unlock time, so a price drop after initiation reduces the payout. [4](#0-3) 

`instantWithdrawal` has no such minimum-of-two protection — the payout is computed once, at execution time, using whatever stale price is stored. [5](#0-4) 

---

### Impact Explanation

A user who calls `instantWithdrawal()` while `rsETHPrice` is stale (higher than the true post-slash value) burns rsETH at an inflated rate and receives more underlying assets than their rsETH is currently worth. The excess assets come from the `LRTUnstakingVault`. When `updateRSETHPrice()` is eventually called, the rsETH price drops to reflect the slash, and the remaining rsETH holders absorb the full loss that the exiting user avoided. This is a direct transfer of slash losses from the exiting user to all remaining holders.

**Impact: High — Theft of unclaimed yield / principal from remaining rsETH holders.**

---

### Likelihood Explanation

EigenLayer operator slashing is an explicitly anticipated risk for restaking protocols. The window between a slash event (on-chain, observable via EigenLayer events) and the next `updateRSETHPrice()` call is non-zero and unpredictable — price updates are not atomic with slashes. Any user monitoring EigenLayer slash events can call `instantWithdrawal()` within this window without needing to front-run any specific pending transaction. The `instantWithdrawal` feature is manager-enabled per asset and is a live production path. [6](#0-5) 

---

### Recommendation

Call `updateRSETHPrice()` (or an equivalent internal price refresh) atomically at the start of `instantWithdrawal()` before computing `getExpectedAssetAmount`. This mirrors the fix applied in the referenced report: ensure the price reflects any pending losses before allowing a user to exit.

```solidity
function instantWithdrawal(...) external ... {
    // Refresh price before computing payout
    ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE)).updateRSETHPrice();
    
    uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
    ...
}
```

Alternatively, adopt the same minimum-of-two protection used in `_calculatePayoutAmount` for the queued withdrawal path.

---

### Proof of Concept

1. EigenLayer slashes an operator, reducing `getEffectivePodShares()` across one or more `NodeDelegator` contracts. The true rsETH price is now lower than `LRTOracle.rsETHPrice`.
2. `updateRSETHPrice()` has not yet been called; `rsETHPrice` remains at the pre-slash value.
3. Attacker holds `R` rsETH. They call `instantWithdrawal(asset, R, "")`.
4. `getExpectedAssetAmount` computes `payout = R × rsETHPrice_stale / assetPrice`, which is larger than `R × rsETHPrice_true / assetPrice`.
5. Attacker receives the inflated payout from `LRTUnstakingVault`; their rsETH is burned.
6. `updateRSETHPrice()` is called; `rsETHPrice` drops to reflect the slash. All remaining rsETH holders now hold tokens worth less — they absorbed the attacker's share of the slash loss. [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L55-56)
```text
    mapping(address asset => bool) public isInstantWithdrawalEnabled;
    uint256 public instantWithdrawalFee; // Fee in basis points (1 = 0.01%)
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

**File:** contracts/LRTWithdrawalManager.sol (L824-835)
```text
    function _calculatePayoutAmount(
        WithdrawalRequest storage request,
        uint256 rsETHPrice,
        uint256 assetPrice
    )
        private
        view
        returns (uint256)
    {
        uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
        return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L214-251)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }

        if (highestRsethPrice == 0) {
            highestRsethPrice = rsETHPrice;
        }

        uint256 previousPrice = rsETHPrice;

        // get total ETH in the protocol (normalized to 1e18)
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

```

**File:** contracts/LRTOracle.sol (L329-349)
```text
    /// @notice get total ETH in protocol
    /// @return totalETHInProtocol total ETH in protocol (normalized to 1e18)
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

            unchecked {
                ++assetIdx;
            }
        }
    }
```
