### Title
Missing Minimum Return Check in `instantWithdrawal` Allows rsETH to Be Burned for Zero Asset Return - (File: contracts/LRTWithdrawalManager.sol)

### Summary
`LRTWithdrawalManager.instantWithdrawal` computes `assetAmountUnlocked` via integer division and then deducts a fee to produce `userAmount`, but never verifies that `userAmount > 0` before permanently burning the caller's rsETH. If the division truncates to zero, the user's rsETH is destroyed and they receive nothing.

### Finding Description
In `instantWithdrawal`, the asset amount is computed as:

```solidity
uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
// getExpectedAssetAmount: amount * rsETHPrice / assetPrice
``` [1](#0-0) 

Then rsETH is burned unconditionally before any check on the resulting value:

```solidity
IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
``` [2](#0-1) 

After the burn, the fee and user amount are computed:

```solidity
uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;
uint256 userAmount = assetAmountUnlocked - fee;
// ...
_transferAsset(asset, msg.sender, userAmount);
``` [3](#0-2) 

There is no guard that `userAmount > 0` (or `assetAmountUnlocked > 0`) before the burn executes. The only pre-condition is:

```solidity
if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
    revert InvalidAmountToWithdraw();
}
``` [4](#0-3) 

`minRsEthAmountToWithdraw[asset]` is a mapping that defaults to `0`, so the only enforced lower bound is `rsETHUnstaked != 0`. A user can pass `rsETHUnstaked = 1` (1 wei), and if `rsETHPrice < assetPrice` (e.g., a newly supported LST priced above rsETH), integer division yields `assetAmountUnlocked = 0`, `fee = 0`, `userAmount = 0`. The rsETH is already burned at that point.

The `getExpectedAssetAmount` formula:

```solidity
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
``` [5](#0-4) 

truncates to zero whenever `rsETHUnstaked * rsETHPrice < assetPrice`.

### Impact Explanation
The user's rsETH is permanently burned and they receive zero underlying assets. The contract fails to deliver the promised return. This maps to **Low — Contract fails to deliver promised returns, but doesn't lose value** (though in practice the rsETH principal is destroyed, making the loss real for the caller).

### Likelihood Explanation
Likelihood is low under current asset configuration (ETH, stETH, ETHx all price below rsETH), but becomes reachable if:
1. `minRsEthAmountToWithdraw[asset]` is left at its default of `0` for a newly added asset, AND
2. That asset's oracle price exceeds `rsETHPrice` (e.g., a high-value LST or yield-bearing token).

Both conditions are plausible during protocol expansion. An unprivileged user triggers this with a single `instantWithdrawal` call.

### Recommendation
Add a minimum return check before burning rsETH:

```solidity
uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
if (assetAmountUnlocked == 0) revert InvalidAmountToWithdraw();
// ... then burn
```

Additionally, enforce a non-zero `minRsEthAmountToWithdraw` for every asset before enabling instant withdrawal, so that integer-division truncation to zero is structurally impossible.

### Proof of Concept
1. Admin adds a new LST whose oracle price is `2e18` (2 ETH per token). `rsETHPrice = 1.05e18`.
2. Admin enables instant withdrawal for the asset but leaves `minRsEthAmountToWithdraw[asset] = 0`.
3. User calls `instantWithdrawal(asset, 1, "")` (1 wei of rsETH).
4. `assetAmountUnlocked = 1 * 1.05e18 / 2e18 = 0` (integer truncation).
5. `burnFrom(user, 1)` executes — 1 wei rsETH is destroyed.
6. `unstakingVault.redeem(asset, 0)` is a no-op.
7. `fee = 0`, `userAmount = 0`.
8. `_transferAsset(asset, user, 0)` — user receives nothing.
9. Net result: user loses 1 wei of rsETH with zero asset received. [6](#0-5)

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

**File:** contracts/LRTWithdrawalManager.sol (L593-593)
```text
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```
