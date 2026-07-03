### Title
Missing Minimum Output Slippage Guard in L2 Pool `deposit()` Functions Allows Users to Receive Fewer wrsETH Than Expected - (File: contracts/pools/RSETHPoolV3ExternalBridge.sol)

### Summary
All L2 liquidity pool `deposit()` functions (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPoolNoWrapper`) accept ETH or LST tokens and mint wrsETH/rsETH based on the live oracle rate at execution time, but provide no `minRSETHAmountExpected` parameter. If the oracle rate is updated between tx submission and execution, users silently receive fewer wrsETH tokens than they observed when constructing the transaction. The L1 `LRTDepositPool` already has this protection; the L2 pools do not.

### Finding Description
`LRTDepositPool.depositETH()` and `depositAsset()` on L1 both accept a `minRSETHAmountExpected` parameter and revert in `_beforeDeposit()` if the minted amount falls below it:

```solidity
// LRTDepositPool.sol:76-93
function depositETH(uint256 minRSETHAmountExpected, string calldata referralId)
    external payable ...
{
    uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);
    _mintRsETH(rsethAmountToMint);
}
``` [1](#0-0) 

```solidity
// LRTDepositPool.sol:667-669
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
``` [2](#0-1) 

The L2 pool equivalents have no such guard. In `RSETHPoolV3ExternalBridge`, both ETH and token deposit paths compute the output amount from the live oracle rate and immediately mint, with no floor check:

```solidity
// RSETHPoolV3ExternalBridge.sol:366-384
function deposit(string memory referralId) external payable ... {
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);   // no minimum check
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
``` [3](#0-2) 

```solidity
// RSETHPoolV3ExternalBridge.sol:390-412
function deposit(address token, uint256 amount, string memory referralId) external ... {
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);   // no minimum check
}
``` [4](#0-3) 

The rate used is fetched live from the oracle at execution time:

```solidity
// RSETHPoolV3ExternalBridge.sol:418-427
function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    uint256 rsETHToETHrate = getRate();          // live oracle read
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
``` [5](#0-4) 

The same pattern is present in `RSETHPoolV3`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPoolNoWrapper`, and `RSETHPool`. [6](#0-5) [7](#0-6) 

### Impact Explanation
When the cross-chain oracle rate is updated (via LayerZero from L1 to L2) between the moment a user observes the rate and the moment their transaction is included, the user receives fewer wrsETH tokens than they expected for the same ETH/LST input. Because the fee is deducted from the input regardless of the rate, the user bears the full fee cost while receiving a reduced token output. The contract fails to deliver the token quantity the user was promised at the time of submission.

**Impact: Low** — Contract fails to deliver promised returns, but does not cause a direct loss of ETH value (the fewer tokens received are each worth proportionally more ETH).

### Likelihood Explanation
The L2 oracle rate is updated by the `CrossChainRateReceiver` / `MultiChainRateProvider` infrastructure via LayerZero messages, which are sent periodically as rsETH accrues staking rewards. Any user transaction that is pending in the mempool during a rate update will silently receive fewer tokens. On chains with variable block times or congestion, this window can be several minutes. No adversarial action is required; normal protocol operation is sufficient to trigger the discrepancy.

### Recommendation
Add a `uint256 minRSETHAmountExpected` parameter to all L2 pool `deposit()` functions, mirroring the protection already present in `LRTDepositPool`. After computing `rsETHAmount`, revert if it is below the caller-supplied minimum:

```solidity
function deposit(string memory referralId, uint256 minRSETHAmountExpected)
    external payable nonReentrant whenNotPaused limitDailyMint(msg.value, ETH_IDENTIFIER)
{
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRSETHAmountExpected) revert MinimumAmountToReceiveNotMet();
    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
```

Apply the same change to the token-deposit overload and to all other pool variants.

### Proof of Concept
1. User calls `RSETHPoolV3ExternalBridge.viewSwapRsETHAmountAndFee(1 ether)` and observes they will receive `X` wrsETH at the current rate of `R`.
2. User submits `deposit{value: 1 ether}("ref")`.
3. Before the tx is mined, the `CrossChainRateReceiver` delivers a LayerZero message that updates the oracle rate from `R` to `R'` (where `R' > R`, reflecting new staking rewards).
4. The user's tx executes: `rsETHAmount = 0.999 ether * 1e18 / R'`, which is less than `X`.
5. `wrsETH.mint(msg.sender, rsETHAmount)` mints the reduced amount with no revert.
6. The user receives fewer wrsETH than they observed, with no recourse. The same fee was charged.

### Citations

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

**File:** contracts/LRTDepositPool.sol (L665-669)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
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
