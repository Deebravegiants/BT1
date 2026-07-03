### Title
Missing Minimum Amount Out (Slippage Protection) in L2 Pool `deposit` Functions - (`contracts/pools/RSETHPoolV3.sol`, `contracts/pools/RSETHPoolV3ExternalBridge.sol`)

---

### Summary

The `deposit` functions in `RSETHPoolV3.sol` and `RSETHPoolV3ExternalBridge.sol` accept ETH or supported tokens and mint wrsETH to the caller based on the oracle rate at execution time. Neither function accepts a `minRsETHAmountExpected` parameter, leaving users with no on-chain slippage protection. This is in direct contrast to the L1 entry point (`LRTDepositPool`), which enforces a `minRSETHAmountExpected` check on every deposit.

---

### Finding Description

`RSETHPoolV3.deposit(string)` (ETH path) and `RSETHPoolV3.deposit(address,uint256,string)` (token path) compute the wrsETH amount to mint entirely from the live oracle rate at the moment of execution:

```solidity
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
// ...
wrsETH.mint(msg.sender, rsETHAmount);
```

`viewSwapRsETHAmountAndFee` divides by `getRate()`, which is a single live call to `IOracle(rsETHOracle).getRate()`. There is no floor on `rsETHAmount` that the caller can specify. The identical pattern exists in `RSETHPoolV3ExternalBridge.deposit`.

By contrast, the L1 deposit pool enforces:

```solidity
rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
```

The same gap exists on the withdrawal side: `LRTWithdrawalManager.instantWithdrawal` burns rsETH and transfers assets with no `minAmountOut` parameter, computing the payout entirely from live oracle prices at execution time.

---

### Impact Explanation

If the oracle rate is updated between the block in which a user's transaction is submitted and the block in which it is included, the user receives fewer wrsETH tokens than they observed when constructing the transaction. Because the rsETH/ETH rate is a monotonically increasing accumulator (staking rewards), any oracle refresh that occurs during a period of high network congestion or deliberate transaction delay will silently reduce the user's output. The user has no on-chain mechanism to reject the execution if the output falls below their acceptable threshold.

**Impact:** Low — contract fails to deliver the promised return observed at submission time, but does not result in direct fund loss (the deposited ETH/token is still represented by the minted wrsETH at the updated rate).

---

### Likelihood Explanation

The L2 pools are the primary retail entry point for the protocol. Oracle rates update on every Chainlink heartbeat (typically every 24 hours or on a 0.5% deviation trigger). During periods of high gas prices, user transactions can sit in the mempool for multiple blocks, spanning one or more oracle updates. This is a routine, non-adversarial scenario that affects ordinary users without any attacker involvement.

---

### Recommendation

Add a `minRsETHAmountExpected` parameter to both `deposit` overloads in `RSETHPoolV3` and `RSETHPoolV3ExternalBridge`, mirroring the pattern already used in `LRTDepositPool._beforeDeposit`:

```solidity
function deposit(
    string memory referralId,
    uint256 minRsETHAmountExpected   // <-- add this
) external payable nonReentrant whenNotPaused limitDailyMint(msg.value, ETH_IDENTIFIER) {
    // ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmountExpected) revert SlippageExceeded();
    wrsETH.mint(msg.sender, rsETHAmount);
}
```

Apply the same fix to `instantWithdrawal` in `LRTWithdrawalManager`, adding a `minAssetAmountExpected` parameter checked against `userAmount` before the transfer.

---

### Proof of Concept

1. User observes `getRate()` = 1.05 ETH/rsETH on `RSETHPoolV3` and submits `deposit{value: 1 ether}("ref")` expecting ≈ 0.952 wrsETH.
2. Before the transaction is mined, a Chainlink oracle heartbeat updates `getRate()` to 1.06 ETH/rsETH.
3. The transaction executes: `rsETHAmount = 1e18 * 1e18 / 1.06e18 ≈ 0.943 wrsETH` — roughly 1% less than expected, with no revert.
4. The user has no recourse; the L1 equivalent (`LRTDepositPool.depositETH`) would have reverted with `MinimumAmountToReceiveNotMet` if the user had passed `minRSETHAmountExpected = 0.952e18`.

**Relevant code locations:**

`RSETHPoolV3.deposit` (ETH, no minimum out): [1](#0-0) 

`RSETHPoolV3.deposit` (token, no minimum out): [2](#0-1) 

`RSETHPoolV3ExternalBridge.deposit` (ETH, no minimum out): [3](#0-2) 

`RSETHPoolV3ExternalBridge.deposit` (token, no minimum out): [4](#0-3) 

`LRTDepositPool._beforeDeposit` (L1 equivalent — has the check): [5](#0-4) 

`LRTWithdrawalManager.instantWithdrawal` (withdrawal side, no minimum out): [6](#0-5)

### Citations

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

**File:** contracts/pools/RSETHPoolV3.sol (L271-293)
```text
    function deposit(
        address token,
        uint256 amount,
        string memory referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedToken(token)
        limitDailyMint(amount, token)
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L366-384)
```text
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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L390-412)
```text
    function deposit(
        address token,
        uint256 amount,
        string memory referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedToken(token)
        limitDailyMint(amount, token)
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
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
