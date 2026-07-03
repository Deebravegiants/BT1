### Title
Missing `minAmountOut` Slippage Protection in L2 Pool Deposit Functions - (File: contracts/pools/RSETHPoolV3.sol, contracts/pools/RSETHPoolV3ExternalBridge.sol, contracts/pools/RSETHPoolV3WithNativeChainBridge.sol, contracts/pools/RSETHPoolV2.sol, contracts/pools/RSETHPoolV2ExternalBridge.sol)

---

### Summary

Every L2 pool `deposit()` function accepts ETH or LST tokens and mints wrsETH to the caller, but none of them accept a `minAmountOut` parameter. Users have no on-chain mechanism to enforce a minimum acceptable wrsETH amount, leaving them exposed to oracle rate changes that occur between the time they preview the swap and the time their transaction executes. By contrast, the L1 `LRTDepositPool.depositAsset()` function explicitly accepts and enforces `minRSETHAmountExpected`.

---

### Finding Description

The `deposit()` functions across all L2 pool variants compute the wrsETH output amount at execution time using a live oracle rate:

**`RSETHPoolV3.sol` (ETH path, line 246–264):**
```solidity
function deposit(string memory referralId) external payable ... {
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);   // no minimum enforced
}
```

**`RSETHPoolV3.sol` (token path, line 271–293):**
```solidity
function deposit(address token, uint256 amount, string memory referralId) external ... {
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
    feeEarnedInToken[token] += fee;
    wrsETH.mint(msg.sender, rsETHAmount);   // no minimum enforced
}
```

The rate computation inside `viewSwapRsETHAmountAndFee` reads the live oracle:
```solidity
uint256 rsETHToETHrate = getRate();                                    // live oracle
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate(); // live oracle
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

The same pattern is present in `RSETHPoolV3ExternalBridge.sol` (lines 366–412), `RSETHPoolV3WithNativeChainBridge.sol` (lines 282–329), `RSETHPoolV2.sol`, and `RSETHPoolV2ExternalBridge.sol` (line 289–301).

The L1 counterpart, `LRTDepositPool.depositAsset()`, explicitly guards against this:
```solidity
function depositAsset(address asset, uint256 depositAmount,
    uint256 minRSETHAmountExpected, string calldata referralId) ...
{
    rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
    if (rsethAmountToMint < minRSETHAmountExpected)
        revert MinimumAmountToReceiveNotMet();
}
```

The L2 pools provide no equivalent guard.

---

### Impact Explanation

A depositor calls `viewSwapRsETHAmountAndFee` off-chain to preview the wrsETH they will receive, then submits the `deposit()` transaction. If the oracle rate updates between preview and execution (a routine event as rsETH accrues restaking rewards, or as a supported LST oracle ticks), the user receives fewer wrsETH than they expected with no revert and no recourse. The deposited ETH or LST is fully consumed; the user simply receives a smaller share position than anticipated.

Impact: **Low** — "Contract fails to deliver promised returns, but doesn't lose value." The user's deposited assets are not stolen; they receive wrsETH, just less than the amount they previewed. However, for large deposits or during periods of rapid oracle movement, the shortfall can be material.

---

### Likelihood Explanation

Oracle rates for rsETH and supported LSTs (e.g., wstETH) update regularly. Any deposit transaction that is pending in the mempool for more than one block is exposed to a rate tick. This is a routine, non-adversarial condition. No attacker action is required; the exposure is inherent to every deposit call on every L2 pool variant.

---

### Recommendation

Add a `minWrsETHAmountExpected` parameter to all `deposit()` overloads in every L2 pool contract, mirroring the pattern already used in `LRTDepositPool.depositAsset()`:

```solidity
function deposit(string memory referralId, uint256 minWrsETHAmountExpected)
    external payable nonReentrant whenNotPaused ...
{
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(msg.value);
    if (rsETHAmount < minWrsETHAmountExpected) revert MinimumAmountToReceiveNotMet();
    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);
}
```

Apply the same change to the token-deposit overload and to all pool variants (`RSETHPoolV2`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`).

---

### Proof of Concept

1. Alice calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain and sees she will receive `X` wrsETH.
2. Alice submits `deposit{value: 1 ether}("ref")`.
3. Before Alice's transaction is mined, the rsETH oracle updates (routine reward accrual), increasing `rsETHToETHrate`.
4. Alice's transaction executes. `rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate` is now smaller than `X`.
5. `wrsETH.mint(msg.sender, rsETHAmount)` mints the reduced amount with no revert.
6. Alice receives fewer wrsETH than she previewed, with no on-chain protection.

Contrast: on L1, step 4 would revert with `MinimumAmountToReceiveNotMet()` if `rsethAmountToMint < minRSETHAmountExpected`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

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

**File:** contracts/pools/RSETHPoolV3.sol (L299-335)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }

    /// @dev view function to get the rsETH amount for a given amount of token
    /// @param amount The amount of token
    /// @param token The token address
    /// @return rsETHAmount The amount of rsETH that will be received
    /// @return fee The fee that will be charged
    function viewSwapRsETHAmountAndFee(
        uint256 amount,
        address token
    )
        public
        view
        onlySupportedToken(token)
        returns (uint256 rsETHAmount, uint256 fee)
    {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L366-412)
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

    /// @dev Swaps supported token for rsETH
    /// @param token The token address
    /// @param amount The amount of token
    /// @param referralId The referral id
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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L282-329)
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

    /// @dev Swaps supported token for rsETH
    /// @param token The token address
    /// @param amount The amount of token
    /// @param referralId The referral id
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
