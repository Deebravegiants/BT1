### Title
No Slippage or Deadline Protection in L2 Pool `deposit()` Functions - (`contracts/pools/RSETHPoolV3.sol`)

### Summary
All L2 pool `deposit()` functions compute the wrsETH/rsETH output amount at execution time using a live oracle rate, but accept no `minOutAmount` or `deadline` parameter from the caller. A user's transaction can sit in the mempool and execute after an oracle rate update, silently delivering fewer tokens than the user expected when they submitted the transaction.

### Finding Description
Every pool variant's `deposit()` function fetches the current oracle rate at execution time and mints/transfers wrsETH or rsETH proportional to that rate:

```solidity
// RSETHPoolV3.sol deposit(string)
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
// ...
wrsETH.mint(msg.sender, rsETHAmount);
```

`viewSwapRsETHAmountAndFee` calls `getRate()` live:

```solidity
uint256 rsETHToETHrate = getRate(); // live oracle read
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

The oracle rate is pushed cross-chain by `MultiChainRateProvider` / `CrossChainRateReceiver` and can be updated at any time. If the rate increases between the moment a user previews the swap and the moment the transaction is mined, the user receives fewer wrsETH than expected, with no on-chain protection. There is also no `deadline` parameter, so a transaction that is delayed in the mempool (e.g., due to low gas price) can execute long after the user intended, at a materially different rate.

This pattern is present in every pool contract:
- `RSETHPoolV3.sol` — `deposit(string)` and `deposit(address,uint256,string)`
- `RSETHPoolV3ExternalBridge.sol` — same two overloads
- `RSETHPoolV3WithNativeChainBridge.sol` — same two overloads
- `RSETHPool.sol` — same two overloads
- `RSETHPoolNoWrapper.sol` — same two overloads
- `RSETHPoolV2ExternalBridge.sol` — `deposit(string)`

### Impact Explanation
A user who previews a deposit via `viewSwapRsETHAmountAndFee` and then submits a transaction may receive materially fewer wrsETH/rsETH than the preview showed if the oracle rate is updated before the transaction is included. The user has no on-chain recourse because there is no minimum-output check. This maps to **Low: Contract fails to deliver promised returns, but doesn't lose value** (the user's ETH/LST is consumed but fewer LRT shares are minted than expected).

### Likelihood Explanation
The oracle rate is updated regularly via the cross-chain rate infrastructure. On L2 networks with variable block times or congested mempools, a transaction can easily be delayed by minutes to hours. Any oracle update during that window silently changes the output amount. This is a normal operational condition, not an edge case.

### Recommendation
Add a `minRsETHAmountOut` parameter to each `deposit()` overload and revert if the computed `rsETHAmount` is below it. Optionally add a `deadline` parameter and revert if `block.timestamp > deadline`.

```solidity
function deposit(string memory referralId, uint256 minRsETHAmountOut) external payable {
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmountOut) revert SlippageExceeded();
    ...
}
```

### Proof of Concept
1. User calls `viewSwapRsETHAmountAndFee(1 ether)` off-chain. Oracle rate is `1.05e18` → preview shows `~0.952 wrsETH`.
2. User submits `deposit{value: 1 ether}("ref")` with a low gas price.
3. Before the tx is mined, the oracle rate is updated to `1.10e18` (rsETH appreciated).
4. Tx executes: `rsETHAmount = 1e18 * 1e18 / 1.10e18 = ~0.909 wrsETH`.
5. User receives `~0.909 wrsETH` instead of the expected `~0.952 wrsETH` — a ~4.5% shortfall — with no revert.

The live oracle read with no output guard is the root cause: [1](#0-0) [2](#0-1) 

The same pattern repeats across all pool variants: [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L258-263)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

```

**File:** contracts/pools/RSETHPoolV3.sol (L299-307)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L237-243)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
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
