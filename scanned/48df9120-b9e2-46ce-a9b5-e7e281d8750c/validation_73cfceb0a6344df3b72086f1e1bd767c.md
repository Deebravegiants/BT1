### Title
Missing Deadline and Minimum Output Protection in `deposit()` Allows Transaction Displacement — (File: `contracts/pools/RSETHPool.sol`, `contracts/pools/RSETHPoolV2.sol`, `contracts/pools/RSETHPoolV3.sol`, `contracts/pools/RSETHPoolV3ExternalBridge.sol`, `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol`)

---

### Summary

The `deposit()` functions across all RSETHPool variants accept ETH or supported tokens from users and return rsETH (or wrsETH) calculated from a live oracle rate at execution time. None of these functions accept a `deadline` parameter or a `minRsETHAmount` (minimum output) parameter. A transaction submitted by a user can sit in the mempool and execute at a later block when the oracle rate has moved unfavorably, causing the user to receive fewer rsETH than they expected at submission time, with no on-chain protection.

---

### Finding Description

Every `deposit()` entry point in the RSETHPool family follows the same pattern:

```solidity
// RSETHPoolV3.sol (representative)
function deposit(string memory referralId)
    external payable nonReentrant whenNotPaused
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

The rsETH output is computed entirely from the oracle rate at execution time:

```solidity
function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
    fee = amount * feeBps / 10_000;
    uint256 amountAfterFee = amount - fee;
    uint256 rsETHToETHrate = getRate();          // live oracle read
    rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
}
```

Because rsETH is a yield-bearing token, its ETH-denominated rate (`rsETHToETHrate`) increases monotonically over time as staking rewards accrue. A transaction that is delayed — whether due to low gas price, network congestion, or sequencer reordering — executes against a higher rate, producing a strictly smaller `rsETHAmount` for the same ETH input. The user has no on-chain mechanism to express a minimum acceptable output or a latest acceptable block/timestamp.

The same pattern applies to the token-denominated overload:

```solidity
function deposit(address token, uint256 amount, string memory referralId)
    external nonReentrant whenNotPaused onlySupportedToken(token)
    limitDailyMint(amount, token)
{
    IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
    feeEarnedInToken[token] += fee;
    wrsETH.mint(msg.sender, rsETHAmount);
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
}
```

Here the output also depends on `IOracle(supportedTokenOracle[token]).getRate()`, which can change independently of the rsETH rate, introducing additional rate-change exposure.

Affected files (all share the identical pattern):
- `contracts/pools/RSETHPool.sol`
- `contracts/pools/RSETHPoolNoWrapper.sol`
- `contracts/pools/RSETHPoolV2.sol`
- `contracts/pools/RSETHPoolV2ExternalBridge.sol`
- `contracts/pools/RSETHPoolV2NBA.sol`
- `contracts/pools/RSETHPoolV3.sol`
- `contracts/pools/RSETHPoolV3ExternalBridge.sol`
- `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol`

---

### Impact Explanation

A user who submits a `deposit()` transaction expecting to receive `X` rsETH for `Y` ETH will receive fewer than `X` rsETH if the transaction executes in a later block where the oracle rate is higher. The user does not lose their ETH (the contract correctly mints rsETH at the prevailing rate), but the contract fails to deliver the return the user expected at submission time. This maps to:

> **Low — Contract fails to deliver promised returns, but doesn't lose value.**

The shortfall is bounded by the rate increase between submission and execution. For a transaction delayed by one day at a 4 % APY staking yield, the shortfall is approximately 0.011 %. For longer delays (e.g., days of mempool congestion or sequencer downtime), the shortfall grows proportionally. For the token-denominated path, if the token oracle rate also moves, the shortfall can compound.

---

### Likelihood Explanation

The entry path is fully unprivileged: any depositor can call `deposit()`. The condition that triggers the loss — a transaction executing later than the user intended — is a normal network event (gas price competition, L2 sequencer delays, or deliberate low-gas submission). No attacker action is required; the loss occurs passively whenever execution is delayed. Likelihood is **Low-to-Medium** because delayed execution is a routine occurrence, but the per-transaction financial impact is small under normal staking-yield conditions.

---

### Recommendation

1. Add a `uint256 deadline` parameter to each `deposit()` overload and revert if `block.timestamp > deadline`.
2. Add a `uint256 minRsETHAmount` parameter and revert if the computed `rsETHAmount < minRsETHAmount`.

Either protection alone is sufficient; both together match industry best practice (e.g., Uniswap v2/v3 router pattern).

---

### Proof of Concept

1. Alice calls `RSETHPoolV3.deposit{value: 1 ether}("ref")` when `rsETHToETHrate = 1.05e18`, expecting `≈ 0.952 wrsETH`.
2. The transaction sits in the mempool for 30 days (e.g., low gas price during a fee spike).
3. Staking rewards accrue; the oracle is updated to `rsETHToETHrate = 1.054e18`.
4. The transaction executes: `rsETHAmount = 1e18 * 1e18 / 1.054e18 ≈ 0.9488 wrsETH`.
5. Alice receives `≈ 0.9488 wrsETH` instead of the `≈ 0.952 wrsETH` she expected — a shortfall of `≈ 0.0032 wrsETH` with no on-chain recourse.

Relevant code locations: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** contracts/pools/RSETHPoolV3.sol (L315-335)
```text
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
