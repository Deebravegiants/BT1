### Title
No Minimum rsETH Output in L2 Pool `deposit` Functions Exposes Users to Oracle-Rate Slippage - (File: contracts/pools/RSETHPoolV3ExternalBridge.sol)

### Summary
The `deposit` functions across all L2 pool variants (`RSETHPoolV3ExternalBridge`, `RSETHPool`, `RSETHPoolNoWrapper`) accept ETH or LSTs from users and return wrsETH/rsETH calculated from a live oracle rate, but provide no `minRsETHAmountExpected` parameter. If the oracle rate is updated between transaction submission and execution, users silently receive fewer rsETH tokens than they observed off-chain.

### Finding Description
Every user-facing `deposit` entry point in the L2 pools computes the output amount solely from the current oracle rate at execution time, with no caller-supplied floor:

`RSETHPoolV3ExternalBridge.deposit(string)`: [1](#0-0) 

`RSETHPoolV3ExternalBridge.deposit(address,uint256,string)`: [2](#0-1) 

The same pattern exists in `RSETHPool.deposit`: [3](#0-2) 

And in `RSETHPoolNoWrapper.deposit`: [4](#0-3) 

The output is computed as:

```
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate
``` [5](#0-4) 

where `rsETHToETHrate` is fetched live from `rsETHOracle.getRate()`. There is no check that `rsETHAmount >= minRsETHAmountExpected`.

By contrast, the L1 `LRTDepositPool.depositETH` correctly enforces a caller-supplied minimum: [6](#0-5) [7](#0-6) 

### Impact Explanation
A user who previews `viewSwapRsETHAmountAndFee` off-chain and submits a `deposit` transaction may receive materially fewer wrsETH tokens if the oracle rate is updated before their transaction is included. The user's ETH is consumed and they receive wrsETH, but at a worse rate than they agreed to. This constitutes the contract failing to deliver the promised return without any loss of the deposited asset itself.

**Impact: Low** — Contract fails to deliver promised returns, but does not lose deposited value.

### Likelihood Explanation
The `rsETHOracle` rate is pushed cross-chain via `MultiChainRateProvider` / `CrossChainRateReceiver` and can be updated at any time by the protocol operator. On congested L2s, user transactions can remain pending for multiple blocks, during which an oracle update can occur. Any unprivileged depositor calling `deposit` is exposed on every transaction. Likelihood is **Medium** given the frequency of oracle updates and normal L2 mempool delays.

### Recommendation
Add a `minRsETHAmountExpected` parameter to all `deposit` overloads in `RSETHPoolV3ExternalBridge`, `RSETHPool`, and `RSETHPoolNoWrapper`, mirroring the pattern already used in `LRTDepositPool`:

```solidity
function deposit(string memory referralId, uint256 minRsETHAmountExpected)
    external payable nonReentrant whenNotPaused
    limitDailyMint(msg.value, ETH_IDENTIFIER)
{
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmountExpected) revert SlippageExceeded();
    ...
}
```

### Proof of Concept
1. User calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain and observes `rsETHAmount = X`.
2. User submits `deposit{value: 1 ether}("ref")` to `RSETHPoolV3ExternalBridge`.
3. Before the transaction is mined, the protocol pushes a new oracle rate (rsETH appreciated), increasing `rsETHToETHrate`.
4. The transaction executes: `rsETHAmount = 1e18 * 1e18 / newHigherRate < X`.
5. User receives fewer wrsETH than observed, with no revert and no recourse. [5](#0-4) [8](#0-7) [9](#0-8)

### Citations

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

**File:** contracts/pools/RSETHPool.sol (L265-278)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPool.sol (L311-320)
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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L277-286)
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
