### Title
Missing Zero-Fee Check in `instantWithdrawal` Allows Fee-Free Withdrawals When `instantWithdrawalFee` Is Unset - (File: contracts/LRTWithdrawalManager.sol)

### Summary

`LRTWithdrawalManager.instantWithdrawal()` does not revert when `instantWithdrawalFee` is zero. Because `instantWithdrawalFee` is never initialized in `initialize()` and defaults to `0`, any window where instant withdrawals are enabled before the fee is explicitly set allows users to withdraw assets with no fee charged. The `if (fee > 0)` guard silently skips fee collection rather than reverting, directly mirroring the M-3 pattern where a zero-state causes a tax/fee calculation to silently return zero.

### Finding Description

`instantWithdrawalFee` is declared as a storage variable but is never assigned in `initialize()`:

```solidity
function initialize(address lrtConfigAddr) external initializer {
    // ...
    withdrawalDelayBlocks = 8 days / 12 seconds;
    lrtConfig = ILRTConfig(lrtConfigAddr);
    // instantWithdrawalFee is NOT set → defaults to 0
}
``` [1](#0-0) 

The fee setter `setInstantWithdrawalFee` enforces only an upper bound (`> 1000` reverts), with no lower bound, so `0` is always a valid value:

```solidity
function setInstantWithdrawalFee(uint256 feeBasisPoints) external onlyLRTManager {
    if (feeBasisPoints > 1000) revert FeeTooHigh(); // Max 10%
    instantWithdrawalFee = feeBasisPoints;
``` [2](#0-1) 

Inside `instantWithdrawal`, the fee is computed and then guarded by `if (fee > 0)`. When `instantWithdrawalFee == 0`, `fee` evaluates to `0`, the guard is false, no fee is transferred, and the user receives `assetAmountUnlocked` in full:

```solidity
uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;
uint256 userAmount = assetAmountUnlocked - fee;
// ...
if (fee > 0) {
    _transferAsset(asset, feeRecipient, fee);
    emit InstantWithdrawalFeeCollected(msg.sender, asset, fee);
}
_transferAsset(asset, msg.sender, userAmount);
``` [3](#0-2) 

There is also no guard in `setInstantWithdrawalEnabled` that requires `instantWithdrawalFee > 0` before the feature is turned on:

```solidity
function setInstantWithdrawalEnabled(address asset, bool enabled)
    external
    onlySupportedAsset(asset)
    onlyLRTManager
{
    isInstantWithdrawalEnabled[asset] = enabled;
``` [4](#0-3) 

### Impact Explanation

Every user who calls `instantWithdrawal` while `instantWithdrawalFee == 0` receives the full `assetAmountUnlocked` with zero fee deducted. The protocol treasury (or `instantWithdrawalFeeRecipient`) receives nothing. Because `instantWithdrawal` burns rsETH and redeems real assets from `LRTUnstakingVault`, this is a direct, repeatable loss of protocol fee revenue — **theft of unclaimed yield** — for every instant withdrawal executed in the zero-fee state. [5](#0-4) 

### Likelihood Explanation

The zero-fee state is the **default** state of the contract (no initialization). The exploit window opens the moment a manager calls `setInstantWithdrawalEnabled(asset, true)` without having first called `setInstantWithdrawalFee` with a non-zero value. This ordering mistake is realistic during initial deployment or after an upgrade. Additionally, `setInstantWithdrawalFee(0)` is explicitly permitted by the setter, so the state can be re-entered at any time. Any user monitoring the chain can detect the enabled+zero-fee state and drain fee revenue before the manager corrects it. [6](#0-5) 

### Recommendation

1. **Require a non-zero fee before enabling instant withdrawals**: add `if (instantWithdrawalFee == 0) revert FeeNotSet();` inside `setInstantWithdrawalEnabled` when `enabled == true`.
2. **Or revert in `instantWithdrawal` when fee is zero**: add `if (instantWithdrawalFee == 0) revert FeeNotSet();` at the top of `instantWithdrawal`.
3. **Initialize `instantWithdrawalFee` to a sensible default** (e.g., a minimum basis-point value) inside `initialize()`.

### Proof of Concept

```solidity
// 1. Manager enables instant withdrawals without setting a fee
withdrawalManager.setInstantWithdrawalEnabled(ETH_TOKEN, true);
// instantWithdrawalFee is still 0 (default)

// 2. Attacker (any rsETH holder) calls instantWithdrawal repeatedly
for (uint i = 0; i < N; i++) {
    withdrawalManager.instantWithdrawal(ETH_TOKEN, chunkAmount, "");
}
// fee = (assetAmountUnlocked * 0) / 10_000 = 0
// userAmount = assetAmountUnlocked - 0 = assetAmountUnlocked
// Protocol receives 0 fee; attacker receives full asset amount
``` [7](#0-6)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L56-56)
```text
    uint256 public instantWithdrawalFee; // Fee in basis points (1 = 0.01%)
```

**File:** contracts/LRTWithdrawalManager.sol (L88-98)
```text
    /// @notice Initializes the contract
    /// @param lrtConfigAddr LRT config address
    function initialize(address lrtConfigAddr) external initializer {
        UtilLib.checkNonZeroAddress(lrtConfigAddr);
        __Pausable_init();
        __ReentrancyGuard_init();
        withdrawalDelayBlocks = 8 days / 12 seconds;

        lrtConfig = ILRTConfig(lrtConfigAddr);
        emit UpdatedLRTConfig(lrtConfigAddr);
    }
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

**File:** contracts/LRTWithdrawalManager.sol (L360-366)
```text
    function setInstantWithdrawalEnabled(address asset, bool enabled)
        external
        onlySupportedAsset(asset)
        onlyLRTManager
    {
        isInstantWithdrawalEnabled[asset] = enabled;
        emit InstantWithdrawalEnabledUpdated(asset, enabled);
```

**File:** contracts/LRTWithdrawalManager.sol (L372-375)
```text
    function setInstantWithdrawalFee(uint256 feeBasisPoints) external onlyLRTManager {
        if (feeBasisPoints > 1000) revert FeeTooHigh(); // Max 10%
        instantWithdrawalFee = feeBasisPoints;
        emit InstantWithdrawalFeeUpdated(feeBasisPoints);
```
