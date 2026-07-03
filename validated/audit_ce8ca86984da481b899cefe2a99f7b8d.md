### Title
No Minimum Output (Slippage) Protection in `instantWithdrawal()` and L2 Pool `deposit()` Functions - (File: contracts/LRTWithdrawalManager.sol)

### Summary
The `instantWithdrawal()` function in `LRTWithdrawalManager.sol` and the `deposit()` functions across all L2 pool contracts (`RSETHPool.sol`, `RSETHPoolV3.sol`, `RSETHPoolV3ExternalBridge.sol`, `RSETHPoolNoWrapper.sol`) compute output amounts solely from oracle prices at execution time, with no user-supplied minimum output parameter. Users can receive materially fewer assets or rsETH tokens than anticipated if the oracle rate moves between transaction submission and on-chain execution.

### Finding Description

**`instantWithdrawal()` — `LRTWithdrawalManager.sol`**

The function burns the caller's rsETH and immediately transfers an asset amount derived entirely from two oracle reads:

```solidity
uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
```

`getExpectedAssetAmount` is:

```solidity
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

The rsETH burn is irreversible. There is no `minAssetAmountExpected` parameter, so the user has no on-chain protection against an unfavourable oracle snapshot at execution time. The fee is then deducted on top of this already oracle-dependent amount, compounding the exposure.

**L2 Pool `deposit()` functions**

Every L2 pool variant exposes the same gap. For example, in `RSETHPoolV3ExternalBridge.sol`:

```solidity
function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value, ETH_IDENTIFIER) {
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    ...
    wrsETH.mint(msg.sender, rsETHAmount);
}
```

`viewSwapRsETHAmountAndFee` reads `getRate()` from `rsETHOracle` at execution time:

```solidity
uint256 rsETHToETHrate = getRate();
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

No `minRsETHAmountExpected` parameter exists. The same pattern is present in `RSETHPool.deposit()`, `RSETHPoolV3.deposit()`, and `RSETHPoolNoWrapper.deposit()`.

**Contrast with L1 deposit pool**

The L1 `LRTDepositPool` already enforces slippage protection via `minRSETHAmountExpected` in both `depositETH()` and `depositAsset()`, demonstrating the protocol's awareness of the need for such a guard. The L2 pools and `instantWithdrawal()` are the unprotected paths.

### Impact Explanation
**Low — Contract fails to deliver promised returns, but doesn't lose value.**

Users burning rsETH in `instantWithdrawal()` or depositing ETH/LSTs into L2 pools receive fewer assets or fewer wrsETH/rsETH tokens than the rate they observed off-chain. For `instantWithdrawal()` the rsETH burn is irreversible, so the shortfall cannot be recovered. For L2 pool deposits the user holds fewer rsETH tokens than expected, representing a real reduction in their proportional claim on protocol assets.

### Likelihood Explanation
**Low-Medium.**

The rsETH oracle rate is not freely manipulable (it reflects staking rewards and slashing), but it is updated periodically and can exhibit discrete jumps. On L2s, block times and mempool dynamics mean a transaction can sit pending long enough for an oracle update to occur between submission and execution. The `instantWithdrawal()` path is additionally exposed to the `getAssetPrice(asset)` oracle for the LST being redeemed, which can fluctuate independently.

### Recommendation

1. Add a `minAssetAmountExpected` parameter to `instantWithdrawal()` and revert if `userAmount < minAssetAmountExpected`.
2. Add a `minRsETHAmountExpected` parameter to each L2 pool `deposit()` overload and revert if the computed `rsETHAmount` falls below it, mirroring the existing guard in `LRTDepositPool._beforeDeposit()`.
3. Optionally add a `deadline` parameter to both paths to protect against indefinitely pending transactions.

### Proof of Concept

**`instantWithdrawal()` scenario:**

1. User observes `rsETHPrice = 1.05e18` and `getAssetPrice(ETH) = 1e18`, expects to receive `1.05 ETH` for `1 rsETH`.
2. Transaction sits in the mempool; oracle updates `rsETHPrice` to `1.02e18`.
3. `instantWithdrawal(ETH_TOKEN, 1e18, "")` executes: `assetAmountUnlocked = 1e18 * 1.02e18 / 1e18 = 1.02 ETH`.
4. After the instant-withdrawal fee (e.g. 0.5%), user receives `≈1.015 ETH` — 3.5% less than expected.
5. rsETH is already burned; no recourse.

**L2 pool deposit scenario:**

1. User observes `getRate() = 1.05e18` (rsETH costs 1.05 ETH), submits `deposit{value: 1.05 ETH}("")`.
2. Oracle updates `getRate()` to `1.08e18` before execution.
3. User receives `1.05e18 * 1e18 / 1.08e18 ≈ 0.972 wrsETH` instead of the expected `1 wrsETH`.
4. No minimum output check reverts the transaction; the shortfall is silently accepted. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L364-384)
```text
    /// @dev Swaps ETH for rsETH
    /// @param referralId The referral id
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L418-427)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L246-265)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L231-244)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L648-670)
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
    }
```
