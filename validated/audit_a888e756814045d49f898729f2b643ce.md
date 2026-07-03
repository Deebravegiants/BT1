### Title
rsETH Holders Can Avoid Slashing Losses by Withdrawing at Stale `rsETHPrice` Before Oracle Update - (File: contracts/LRTWithdrawalManager.sol)

### Summary
`instantWithdrawal` and `initiateWithdrawal` in `LRTWithdrawalManager` compute the user's asset payout using the stored `rsETHPrice` from `LRTOracle`. Because `updateRSETHPrice()` is not called atomically with withdrawals, a window exists between a slashing event reducing actual TVL and the oracle price being updated. Any user who withdraws during this window receives more assets than their proportional share, transferring the loss entirely to remaining rsETH holders.

### Finding Description
`LRTOracle` stores `rsETHPrice` as a state variable updated only when `updateRSETHPrice()` is explicitly called. This function is public but not invoked atomically with any withdrawal path.

`getExpectedAssetAmount` in `LRTWithdrawalManager` reads the stored price directly:

```solidity
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

`instantWithdrawal` uses this value to immediately disburse assets to the caller:

```solidity
uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
...
unstakingVault.redeem(asset, assetAmountUnlocked);
```

When an EigenLayer slashing event reduces the actual TVL, `rsETHPrice` remains at its pre-slash value until `updateRSETHPrice()` is called. During this window, any user calling `instantWithdrawal` burns rsETH at the inflated stored price and receives more underlying assets than their fair share. The `_updateRsETHPrice` downside-protection mechanism only pauses the protocol when the price drop exceeds `pricePercentageLimit`; for slashing events below that threshold, the protocol remains live and the stale price is used for all withdrawals.

### Impact Explanation
Users who withdraw during the stale-price window receive excess assets drawn from `LRTUnstakingVault`. When `updateRSETHPrice()` is eventually called, the lower price is reflected and all remaining rsETH holders bear the full slashing loss, including the portion that should have been borne by the exiting users. This is a direct transfer of value from remaining holders to early exiters.

**Impact: High — Theft of unclaimed yield / proportional loss shifting from exiting users to remaining holders.**

### Likelihood Explanation
EigenLayer slashing events are a known and expected risk for restaking protocols. `updateRSETHPrice()` is called periodically by off-chain bots, not on every block. The window between a slashing event being reflected in on-chain TVL and the oracle price being updated is realistic and non-trivial. Any rsETH holder monitoring EigenLayer events can exploit this without any privileged access — `instantWithdrawal` is an unprivileged, publicly callable function.

### Recommendation
Before computing the payout in `instantWithdrawal` (and optionally `initiateWithdrawal`), call `updateRSETHPrice()` to ensure the price reflects current TVL. Alternatively, compute the payout using a live TVL calculation rather than the stored `rsETHPrice`, or revert if the stored price is older than a configurable staleness threshold.

### Proof of Concept
1. Protocol TVL = 1000 ETH, rsETH supply = 1000, `rsETHPrice` = 1.0 ETH/rsETH.
2. EigenLayer slashing event reduces actual TVL to 990 ETH. `rsETHPrice` is still 1.0 (not yet updated).
3. Alice holds 100 rsETH. She calls `instantWithdrawal(ETH, 100e18, "")`.
4. `getExpectedAssetAmount` returns `100 * 1.0 / 1.0 = 100 ETH` (stale price).
5. Alice receives 100 ETH and burns 100 rsETH. Vault pays out 100 ETH.
6. Remaining TVL = 890 ETH, remaining rsETH supply = 900.
7. `updateRSETHPrice()` is called: new price = 890/900 ≈ 0.9889 ETH/rsETH.
8. Alice avoided her proportional share of the 10 ETH loss (~1 ETH). Remaining 900 holders bear the full 10 ETH loss instead of 9 ETH. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

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

**File:** contracts/LRTOracle.sol (L269-282)
```text
        // downside protection — pause if price drops too far
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
