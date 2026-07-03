### Title
Missing Slippage Protection in `instantWithdrawal()` Allows Users to Receive Fewer Assets Than Expected - (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager.instantWithdrawal()` burns rsETH immediately and calculates the asset payout using the live oracle price at execution time, but provides no `minExpectedAssetAmount` parameter. If `updateRSETHPrice()` (a public, permissionless function) is called between a user's transaction submission and its mining, the user's rsETH is permanently burned for fewer assets than they previewed.

---

### Finding Description

`instantWithdrawal()` computes the asset payout by calling `getExpectedAssetAmount()`, which reads `lrtOracle.rsETHPrice()` — the last stored price — at the moment of execution: [1](#0-0) 

```solidity
uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
```

`getExpectedAssetAmount()` divides by the live oracle price: [2](#0-1) 

The stored `rsETHPrice` is updated by `updateRSETHPrice()`, which is a **public, permissionless** function: [3](#0-2) 

The function signature accepts no minimum output guard: [4](#0-3) 

The code's own NatSpec already acknowledges a related race condition for fees, but not for the oracle price: [5](#0-4) 

By contrast, `LRTDepositPool.depositAsset()` and `depositETH()` correctly accept a `minRSETHAmountExpected` parameter and revert if the minted amount falls below it: [6](#0-5) 

---

### Impact Explanation

A user previews the payout with `getExpectedAssetAmount()`, then submits `instantWithdrawal()`. If `updateRSETHPrice()` executes in the same block (or a block between submission and mining), the stored `rsETHPrice` changes. The user's rsETH is burned irreversibly, and they receive fewer underlying assets than they expected. This constitutes a direct, permanent loss of user funds (the difference between the previewed and actual payout).

**Impact: Medium — Temporary/permanent loss of user funds (theft of unclaimed yield / contract fails to deliver promised returns).**

---

### Likelihood Explanation

`updateRSETHPrice()` is callable by any address at any time. Protocol bots routinely call it. An attacker can also front-run a pending `instantWithdrawal()` transaction by calling `updateRSETHPrice()` immediately before it, if the underlying TVL has naturally decreased (e.g., due to LST price movement or slashing). No privileged access is required. The attack is cheap (one extra transaction) and the victim's rsETH is already burned before the payout is computed.

**Likelihood: Medium.**

---

### Recommendation

Add a `minExpectedAssetAmount` parameter to `instantWithdrawal()` and revert if the computed payout falls below it, mirroring the pattern already used in `depositAsset()`:

```solidity
function instantWithdrawal(
    address asset,
    uint256 rsETHUnstaked,
+   uint256 minExpectedAssetAmount,
    string calldata referralId
) external ... {
    ...
    uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
+   if (assetAmountUnlocked < minExpectedAssetAmount) revert SlippageExceeded();
    IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
    ...
}
```

---

### Proof of Concept

1. User calls `getExpectedAssetAmount(ETH_TOKEN, 1e18)` off-chain and sees they will receive `1.05 ETH`.
2. User submits `instantWithdrawal(ETH_TOKEN, 1e18, "ref")`.
3. Before the transaction is mined, a bot (or attacker) calls `updateRSETHPrice()`. The rsETH price drops due to a recent LST price movement.
4. User's transaction mines. `getExpectedAssetAmount()` now returns `0.98 ETH` using the updated price.
5. `burnFrom` burns the user's `1e18` rsETH permanently.
6. User receives `0.98 ETH` instead of the previewed `1.05 ETH` — a loss of `0.07 ETH` with no recourse. [7](#0-6) [3](#0-2)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L210-211)
```text
    /// @dev Uses the fee set at execution time. Managers can raise it right before this call, making withdrawals cost
    /// more than expected.
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

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTDepositPool.sol (L648-669)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```
