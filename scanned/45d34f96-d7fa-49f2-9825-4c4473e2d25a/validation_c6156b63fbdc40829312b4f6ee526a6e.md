Now I have all the information needed. Let me compare the L1 deposit pool (which has slippage protection) against the L2 pool variants (which do not).

**Key observations:**
- `LRTDepositPool.depositETH(uint256 minRSETHAmountExpected, ...)` and `depositAsset(... uint256 minRSETHAmountExpected, ...)` both enforce a minimum rsETH output via `_beforeDeposit()`.
- All three L2 pool variants (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`) expose `deposit()` functions with no `minWrsETHAmount` parameter.

---

### Title
Deposit functions lack caller-side minimum-output bound, exposing depositors to oracle-rate slippage - (`contracts/pools/RSETHPoolV3.sol`, `contracts/pools/RSETHPoolV3ExternalBridge.sol`, `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol`)

### Summary
All three L2 pool variants compute the `wrsETH` amount to mint from a live oracle rate at execution time and immediately settle the swap, with no caller-provided minimum-output guard. The L1 counterpart (`LRTDepositPool`) explicitly accepts a `minRSETHAmountExpected` parameter and reverts if the minted amount falls below it. The L2 pools provide no equivalent protection.

### Finding Description
In every L2 pool variant the ETH and token deposit paths follow the same pattern:

```solidity
// RSETHPoolV3.sol  (identical pattern in V3ExternalBridge and V3WithNativeChainBridge)
function deposit(string memory referralId) external payable ... {
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);          // no min-output check
}
```

`viewSwapRsETHAmountAndFee` computes the output as:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;   // ETH path
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate; // token path
```

Both `rsETHToETHrate` (from `rsETHOracle`) and `tokenToETHRate` (from `supportedTokenOracle[token]`) are live oracle reads that can change between the block in which a user previews the swap and the block in which the transaction is mined. There is no parameter the caller can supply to bound the minimum `wrsETH` they will accept.

By contrast, the L1 deposit pool enforces:

```solidity
// LRTDepositPool.sol  _beforeDeposit()
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
```

The asymmetry is intentional on L1 but was never carried over to the L2 pools.

Additionally, `RSETHPoolV3ExternalBridge.setFeeBps()` is gated only by `DEFAULT_ADMIN_ROLE` (not a timelock) and allows `feeBps` up to `10_000` (100%), meaning the fee itself is a second unbounded variable that can change the effective output with no caller protection.

### Impact Explanation
A depositor who previews the swap via `viewSwapRsETHAmountAndFee`, then submits a `deposit()` transaction, may receive fewer `wrsETH` than expected if the oracle rate is updated before their transaction is included. Because the ETH/token is already transferred into the pool and `wrsETH` is minted at the new (less favorable) rate, the user receives fewer tokens than the rate they observed. The user does not lose the underlying value (each `wrsETH` is worth more ETH at the higher rate), but the contract fails to deliver the number of tokens the user was promised at preview time.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

### Likelihood Explanation
The `rsETH` oracle rate is updated periodically by the protocol (e.g., on yield accrual events). Any deposit transaction that is pending in the mempool when an oracle update is processed will execute at the new rate. This is a routine, non-adversarial scenario that requires no special attacker capability — it occurs naturally during normal protocol operation. The L1 pool's explicit `minRSETHAmountExpected` parameter confirms the protocol designers are aware of this risk and chose to mitigate it on L1 but omitted the mitigation on L2.

### Recommendation
Add a `minWrsETHAmount` parameter to all `deposit()` overloads in `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolV3WithNativeChainBridge`, and revert if the computed `rsETHAmount` is below it, mirroring the `minRSETHAmountExpected` guard already present in `LRTDepositPool._beforeDeposit()`.

```solidity
function deposit(string memory referralId, uint256 minWrsETHAmount) external payable ... {
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minWrsETHAmount) revert InsufficientOutputAmount();
    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);
}
```

### Proof of Concept
1. Alice calls `viewSwapRsETHAmountAndFee(1 ether)` and observes she will receive `X` wrsETH at the current oracle rate `R`.
2. Alice submits `deposit{value: 1 ether}("ref")`.
3. Before Alice's transaction is mined, the protocol updates the rsETH oracle rate from `R` to `R'` where `R' > R` (rsETH has accrued yield).
4. Alice's transaction executes: `rsETHAmount = 1e18 * 1e18 / R'` which is less than `X`.
5. Alice receives fewer wrsETH than she observed at preview time, with no recourse — there is no parameter she could have set to cause the transaction to revert.

Contrast: on L1, Alice would call `depositETH(X, "ref")` and the transaction would revert with `MinimumAmountToReceiveNotMet()` if the minted amount fell below `X`.

**Affected functions:**
- [1](#0-0) 
- [2](#0-1) 
- [3](#0-2) 
- [4](#0-3) 
- [5](#0-4) 
- [6](#0-5) 
- [7](#0-6) 

**L1 reference (protected):**
- [8](#0-7) 
- [9](#0-8)

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

**File:** contracts/pools/RSETHPoolV3.sol (L299-308)
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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L282-301)
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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L307-329)
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

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
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
