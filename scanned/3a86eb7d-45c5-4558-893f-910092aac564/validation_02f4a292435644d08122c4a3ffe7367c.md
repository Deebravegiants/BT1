### Title
rsETH Tokens Remain Freely Transferable When Protocol Is Paused, Enabling Sale of Non-Redeemable Tokens - (File: contracts/RSETH.sol)

### Summary
The `RSETH` token's `_transfer` function does not enforce the `whenNotPaused` modifier, meaning rsETH can be freely transferred between users even when the protocol is paused. Since `initiateWithdrawal` and `instantWithdrawal` in `LRTWithdrawalManager` are blocked during a pause, a malicious rsETH holder can sell their rsETH on a DEX to buyers who cannot redeem it until the protocol is unpaused.

### Finding Description
In `RSETH.sol`, the `mint` and `burnFrom` functions are correctly guarded by `whenNotPaused`: [1](#0-0) 

However, the overridden `_transfer` function only enforces the per-address block list, with no pause check: [2](#0-1) 

This means that when the RSETH contract is paused, rsETH tokens can still be freely transferred via `transfer()` and `transferFrom()`.

A second, more realistic trigger path exists in `LRTOracle`. When the rsETH price drops beyond the configured threshold, the oracle automatically pauses `LRTDepositPool` and `LRTWithdrawalManager` — but does **not** pause the RSETH token contract: [3](#0-2) 

In contrast, the manual `pauseAll()` in `LRTConfig` does pause RSETH: [4](#0-3) 

In both cases — whether RSETH itself is paused or only `LRTWithdrawalManager` is paused — rsETH transfers remain unrestricted while withdrawal entry points are blocked: [5](#0-4) [6](#0-5) 

### Impact Explanation
A malicious rsETH holder can sell their rsETH on a DEX (Uniswap, Curve, etc.) while `LRTWithdrawalManager` is paused. The buyer receives rsETH tokens that cannot be converted back to ETH or LSTs until the protocol is unpaused. The buyer's funds are temporarily frozen in a non-redeemable state. This matches **Medium — Temporary freezing of funds**.

### Likelihood Explanation
The `LRTOracle` price-drop circuit breaker is an automated, unprivileged-trigger path: any sufficiently large market move causes it to fire, pausing withdrawals while leaving rsETH transferable. A sophisticated rsETH holder who monitors oracle state can front-run the pause by dumping rsETH on a DEX immediately after the price drop is detected but before buyers are aware the withdrawal path is closed. No admin compromise is required; the trigger is a normal market event.

### Recommendation
Override `_beforeTokenTransfer` (or add a `whenNotPaused` check inside `_transfer`) in `RSETH.sol` to block transfers when the token contract is paused. Care must be taken to allow the `LRTWithdrawalManager` to still receive rsETH via `initiateWithdrawal` (which calls `safeTransferFrom`) even during a pause, or to ensure the withdrawal manager address is permanently exempt from the transfer block — analogous to the existing `isPermanentlyExempt` mechanism.

Additionally, the `LRTOracle` automatic pause path should be updated to also pause the RSETH token contract, consistent with what `pauseAll()` already does, so that the two pause mechanisms are symmetric.

### Proof of Concept
1. rsETH price drops sharply; `LRTOracle.updateRSETHPrice()` fires the circuit breaker, pausing `LRTDepositPool` and `LRTWithdrawalManager` but **not** RSETH.
2. Malicious rsETH holder calls `rsETH.transfer(dex, amount)` or sells via a DEX router — succeeds because `_transfer` has no pause check.
3. Victim buyer acquires rsETH on the DEX.
4. Victim calls `LRTWithdrawalManager.initiateWithdrawal(asset, amount, "")` — reverts with `Paused`.
5. Victim calls `LRTWithdrawalManager.instantWithdrawal(asset, amount, "")` — reverts with `Paused`.
6. Victim's rsETH is locked in a non-redeemable state until an admin calls `unpause()` on `LRTWithdrawalManager`, with no on-chain indication to the victim of when (or whether) that will occur.

### Citations

**File:** contracts/RSETH.sol (L229-248)
```text
    function mint(
        address to,
        uint256 amount
    )
        external
        onlyRole(LRTConstants.MINTER_ROLE)
        whenNotPaused
        checkDailyMintLimit(amount)
    {
        _enforceNotBlocked(to);
        _mint(to, amount);
    }

    /// @notice Burns rsETH when called by an authorized caller
    /// @param account the account to burn from
    /// @param amount the amount of rsETH to burn
    function burnFrom(address account, uint256 amount) external onlyRole(LRTConstants.BURNER_ROLE) whenNotPaused {
        _enforceNotBlocked(account);
        _burn(account, amount);
    }
```

**File:** contracts/RSETH.sol (L287-291)
```text
    function _transfer(address from, address to, uint256 amount) internal override {
        _enforceNotBlocked(from);
        _enforceNotBlocked(to);
        super._transfer(from, to, amount);
    }
```

**File:** contracts/LRTOracle.sol (L277-282)
```text
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
```

**File:** contracts/LRTConfig.sol (L262-285)
```text
    function pauseAll() external onlyRole(LRTConstants.PAUSER_ROLE) {
        IPausable lrtDepositPool = IPausable(getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable lrtWithdrawalManager = IPausable(getContract(LRTConstants.LRT_WITHDRAW_MANAGER));
        IPausable lrtOracle = IPausable(getContract(LRTConstants.LRT_ORACLE));
        IPausable rsETHContract = IPausable(rsETH);

        if (!lrtDepositPool.paused()) lrtDepositPool.pause();
        if (!lrtWithdrawalManager.paused()) lrtWithdrawalManager.pause();
        if (!lrtOracle.paused()) lrtOracle.pause();
        if (!rsETHContract.paused()) rsETHContract.pause();

        address[] memory nodeDelegatorQueue = ILRTDepositPool(address(lrtDepositPool)).getNodeDelegatorQueue();
        uint256 nodeDelegatorCount = nodeDelegatorQueue.length;

        for (uint256 i = 0; i < nodeDelegatorCount;) {
            IPausable nodeDelegator = IPausable(nodeDelegatorQueue[i]);
            if (!nodeDelegator.paused()) nodeDelegator.pause();
            unchecked {
                ++i;
            }
        }

        emit PausedAll(msg.sender);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L150-178)
```text
    function initiateWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        override
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L212-222)
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
```
