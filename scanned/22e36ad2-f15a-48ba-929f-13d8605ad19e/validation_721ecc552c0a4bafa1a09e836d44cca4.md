### Title
No User-Controlled Minimum Output Amount in Pool `deposit()` Functions - (File: contracts/pools/RSETHPoolV2.sol)

### Summary
Multiple L2 pool contracts compute the rsETH output amount at execution time using an oracle-derived rate, with no caller-specified minimum output guard. A depositor can receive materially fewer rsETH tokens than anticipated if the oracle rate is updated in a transaction mined before theirs.

### Finding Description
Every `deposit()` entry point across the L2 pool family — `RSETHPoolV2`, `RSETHPoolV2NBA`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPool`, and `RSETHPoolNoWrapper` — computes the rsETH output by calling `viewSwapRsETHAmountAndFee()`, which reads a live oracle rate at execution time:

```solidity
// RSETHPoolV2.sol – deposit()
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
feeEarnedInETH += fee;
wrsETH.mint(msg.sender, rsETHAmount);
``` [1](#0-0) 

```solidity
// viewSwapRsETHAmountAndFee – rate fetched from oracle at call time
uint256 rsETHToETHrate = getRate();          // IOracle(rsETHOracle).getRate()
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [2](#0-1) 

None of these `deposit()` signatures accept a `minRsETHAmount` parameter, so there is no on-chain check that the minted amount meets the caller's expectation.

The token-deposit variant in `RSETHPoolV3` and `RSETHPoolV3ExternalBridge` is doubly exposed: it reads **two** oracle rates — `rsETHToETHrate` and `tokenToETHRate` — both of which can shift independently between submission and execution:

```solidity
uint256 rsETHToETHrate = getRate();
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
``` [3](#0-2) 

The L1 `LRTDepositPool` already enforces this protection correctly — both `depositETH` and `depositAsset` accept and enforce `minRSETHAmountExpected`:

```solidity
function depositETH(uint256 minRSETHAmountExpected, string calldata referralId) ...
    uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);
``` [4](#0-3) 

The L2 pool contracts lack this same protection entirely.

### Impact Explanation
**Low — Contract fails to deliver promised returns.**

A depositor who previews the output via `viewSwapRsETHAmountAndFee()` off-chain and then submits a `deposit()` transaction can receive fewer rsETH tokens than the preview showed if the oracle rate is updated before their transaction is mined. The user's ETH (or ERC-20 token) is consumed in full while the rsETH output silently decreases. No funds are stolen by a third party, but the user does not receive the return the protocol implicitly promised at submission time.

### Likelihood Explanation
**Low.**

The rsETH/ETH oracle rate changes gradually under normal conditions (staking yield accrual). However, the risk is elevated during periods of high L2 mempool congestion, during oracle heartbeat updates, or when a user's transaction is delayed in the mempool. The token-deposit path (two oracle reads) has a higher surface area. The scenario requires no privileged actor — any oracle update transaction mined ahead of the deposit suffices.

### Recommendation
Add a `minRsETHAmount` parameter to every public `deposit()` overload in all pool contracts and revert if the computed output falls below it, mirroring the pattern already used in `LRTDepositPool`:

```solidity
function deposit(string memory referralId, uint256 minRsETHAmount)
    external payable nonReentrant whenNotPaused
{
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmount) revert InsufficientOutputAmount();
    ...
}
```

Apply the same pattern to the token-deposit overloads in `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPool`, and `RSETHPoolNoWrapper`.

### Proof of Concept
1. Alice calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain and sees she will receive `X` rsETH at the current oracle rate `R`.
2. Alice submits `deposit("ref")` with `1 ether`.
3. Before Alice's transaction is mined, an oracle update transaction sets the rsETH/ETH rate to `R' > R` (rsETH is now more expensive in ETH terms).
4. Alice's `deposit()` executes with rate `R'`, computing `rsETHAmount = 1e18 * 1e18 / R' < X`.
5. Alice receives fewer rsETH than previewed with no revert and no recourse. Her full 1 ETH is consumed.

For the token-deposit path in `RSETHPoolV3ExternalBridge`, both the `rsETHToETHrate` and `tokenToETHRate` can shift, compounding the slippage exposure. [5](#0-4)

### Citations

**File:** contracts/pools/RSETHPoolV2.sol (L207-218)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value) {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
```

**File:** contracts/pools/RSETHPoolV2.sol (L225-234)
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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L446-452)
```text
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/LRTDepositPool.sol (L76-92)
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
```
