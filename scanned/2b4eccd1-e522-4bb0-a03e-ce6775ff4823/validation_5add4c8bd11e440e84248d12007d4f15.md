### Title
Zero wrsETH Minted for Non-Zero Deposit Due to Integer Division Rounding - (File: contracts/pools/RSETHPoolV3.sol)

### Summary

All L2 pool contracts (`RSETHPoolV3`, `RSETHPool`, `RSETHPoolNoWrapper`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`) share the same `viewSwapRsETHAmountAndFee` calculation pattern that uses integer division without a zero-output guard. A user depositing a sufficiently small amount of ETH or a supported token will have their assets transferred to the pool while receiving zero `wrsETH` (or `rsETH`) in return.

### Finding Description

The `viewSwapRsETHAmountAndFee` function in every pool contract computes the output amount using plain integer division:

```solidity
// ETH path
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;

// Token path
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

Neither the view function nor the calling `deposit` functions check whether `rsETHAmount == 0` before proceeding. The deposit functions only guard against `amount == 0`:

```solidity
function deposit(string memory referralId) external payable ... {
    ...
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();          // only zero-input guard
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);             // mints 0 with no revert
    ...
}
```

The same pattern is present in the token deposit overload and in every pool variant.

### Impact Explanation

A user who sends a small but non-zero ETH or token amount whose product with the numerator is less than `rsETHToETHrate` will receive zero `wrsETH`/`rsETH`. Their deposited assets remain in the pool contract (credited to the pool's bridgeable balance, not to the user), and they receive nothing in return. The contract fails to deliver the promised return for the deposited value.

**Impact: Low** — Contract fails to deliver promised returns. The lost amount per transaction is bounded by `rsETHToETHrate / 1e18` wei of ETH (roughly 1–2 wei at current rates), so individual losses are negligible. However, the invariant that a non-zero deposit always yields a non-zero output is violated.

### Likelihood Explanation

Any unprivileged depositor can trigger this by calling `deposit` with a sufficiently small `msg.value`. No special setup, front-running, or attacker coordination is required. The condition is met organically whenever `amountAfterFee * 1e18 < rsETHToETHrate` (ETH path) or `amountAfterFee * tokenToETHRate < rsETHToETHrate` (token path). As `rsETHToETHrate` grows over time (rsETH accrues value), the threshold for triggering this condition increases slightly, making it marginally more likely.

### Recommendation

Add a zero-output guard in each `deposit` function after computing `rsETHAmount`:

```solidity
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
if (rsETHAmount == 0) revert InvalidAmount();
```

Apply the same guard to the token deposit overload and to all pool contract variants.

### Proof of Concept

Using `RSETHPoolV3.sol` with `rsETHToETHrate = 1.1e18` (rsETH worth 1.1 ETH) and `feeBps = 0`:

1. Alice calls `deposit{value: 1}("")` — sending 1 wei of ETH.
2. `viewSwapRsETHAmountAndFee(1)` computes:
   - `fee = 1 * 0 / 10_000 = 0`
   - `amountAfterFee = 1`
   - `rsETHAmount = 1 * 1e18 / 1.1e18 = 0` (integer division truncates)
3. `amount == 0` check passes (amount is 1, not 0).
4. `feeEarnedInETH += 0`.
5. `wrsETH.mint(msg.sender, 0)` — mints zero tokens to Alice.
6. Alice's 1 wei is now in the pool's ETH balance, bridgeable to L1. Alice holds no `wrsETH`.

The same applies to the token deposit path when `amountAfterFee * tokenToETHRate < rsETHToETHrate`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

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
