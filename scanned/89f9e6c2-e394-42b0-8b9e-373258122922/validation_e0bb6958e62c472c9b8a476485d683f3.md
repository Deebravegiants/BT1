### Title
Lack of Slippage Protection in L2 Pool `deposit()` Functions - (`contracts/pools/RSETHPoolV3ExternalBridge.sol`)

### Summary
The `deposit()` functions in `RSETHPoolV3ExternalBridge.sol` (and analogous L2 pool contracts) accept ETH or tokens from users and mint wrsETH based on the oracle rate at execution time, but provide no `minRsETHAmountExpected` parameter. If the rsETH/ETH rate increases between transaction submission and execution, users receive fewer wrsETH than anticipated — a direct structural parallel to the Sentiment M-15 finding.

### Finding Description
`RSETHPoolV3ExternalBridge.deposit()` computes the wrsETH amount to mint entirely at execution time by calling `viewSwapRsETHAmountAndFee()`, which reads the live oracle rate via `getRate()`:

```solidity
// contracts/pools/RSETHPoolV3ExternalBridge.sol L366-384
function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(...) {
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
``` [1](#0-0) 

The rate used is `getRate()` → `IOracle(rsETHOracle).getRate()`, which returns the current cross-chain rsETH price pushed from L1. There is no `minRsETHAmount` guard anywhere in the call path. [2](#0-1) 

The same pattern applies to the token-deposit overload:

<cite repo="Tylerpinwa/LRT-rsETH--015" path="contracts/pools/RSETHPoolV3ExternalBridge.sol" start="390" end="412"

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
