### Title
Zero wrsETH Minted on Dust Deposits Due to Missing Zero-Amount Guard - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
The L2 pool deposit functions in `RSETHPoolV3`, `RSETHPoolNoWrapper`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolV3WithNativeChainBridge` compute the wrsETH/rsETH amount to mint via a division that can round to zero for small inputs, yet no guard reverts the transaction when the result is zero. A user who sends a non-zero ETH or token amount receives zero wrsETH in return, losing their deposited assets.

### Finding Description

Every L2 pool's `deposit` function delegates the share calculation to `viewSwapRsETHAmountAndFee`:

**ETH path** (`RSETHPoolV3.sol`, line 307):
```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**Token path** (`RSETHPoolV3.sol`, line 334):
```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

`rsETHToETHrate` is the rsETH/ETH exchange rate returned by the oracle, expressed in 1e18 precision. It starts at 1e18 and grows monotonically as yield accrues. Once `rsETHToETHrate > 1e18` (which is the normal operating state of the protocol), any deposit where `amountAfterFee * 1e18 < rsETHToETHrate` produces `rsETHAmount = 0` due to Solidity integer division truncation.

The deposit functions then proceed unconditionally:

```solidity
// RSETHPoolV3.sol deposit(string)
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
feeEarnedInETH += fee;
wrsETH.mint(msg.sender, rsETHAmount);   // mints 0 — no revert
```

```solidity
// RSETHPoolNoWrapper.sol deposit(string)
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
feeEarnedInETH += fee;
rsETH.safeTransfer(msg.sender, rsETHAmount);  // transfers 0 — no revert
```

There is no `minRSETHAmountExpected` slippage parameter and no `require(rsETHAmount > 0)` guard in any of the four pool variants. The only input validation is `if (amount == 0) revert InvalidAmount()`, which does not protect against zero output.

### Impact Explanation

A user who deposits a dust amount of ETH (e.g., 1 wei) when `rsETHToETHrate > 1e18` has their ETH accepted by the contract, `feeEarnedInETH` is incremented by zero (fee also rounds to zero for 1 wei), and `wrsETH.mint(msg.sender, 0)` is called — the user receives nothing. The deposited ETH is permanently absorbed into the pool's balance, benefiting all existing wrsETH holders. The impact per transaction is limited to dust amounts (1 wei), making this a **Low** severity finding: the contract fails to deliver its promised return (wrsETH) without reverting, causing a small but real loss of user funds.

### Likelihood Explanation

The condition is reachable by any unprivileged caller via the public `deposit` functions on any deployed L2 pool. No special role or front-running is required. The condition activates as soon as `rsETHToETHrate` exceeds 1e18, which is the normal post-launch state of the protocol. Any user who accidentally sends 1 wei (e.g., a scripting error, a test transaction, or a wallet rounding) will silently lose it.

### Recommendation

Add a zero-output guard in each deposit function, mirroring the well-known ERC-4626 pattern:

```solidity
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
require(rsETHAmount != 0, "zero wrsETH minted");
feeEarnedInETH += fee;
wrsETH.mint(msg.sender, rsETHAmount);
```

Apply the same guard to the token deposit path and to all pool variants (`RSETHPoolNoWrapper`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`).

### Proof of Concept

Assume `rsETHToETHrate = 1.05e18` (5 % yield accrued, a realistic near-term value).

1. Alice calls `RSETHPoolV3.deposit{value: 1}("")` (1 wei ETH).
2. `fee = 1 * feeBps / 10_000 = 0` (rounds down).
3. `amountAfterFee = 1 - 0 = 1`.
4. `rsETHAmount = 1 * 1e18 / 1.05e18 = 0` (Solidity truncation).
5. `feeEarnedInETH += 0`.
6. `wrsETH.mint(Alice, 0)` — Alice receives 0 wrsETH.
7. Alice's 1 wei is permanently held in the pool, accruing to existing holders.

The transaction succeeds with no revert, and Alice has no way to detect the outcome before submitting because there is no `minRSETHAmountExpected` parameter.

---

**Root cause lines:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L229-244)
```text
    /// @dev Swaps ETH for rsETH
    /// @param referralId The referral id
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
