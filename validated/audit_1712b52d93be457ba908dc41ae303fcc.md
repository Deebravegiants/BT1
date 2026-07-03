### Title
Missing Minimum Output (Slippage) Check on L2 Pool `deposit()` Functions - (`contracts/pools/RSETHPoolV3.sol`, `contracts/pools/RSETHPoolV3ExternalBridge.sol`, `contracts/pools/RSETHPoolNoWrapper.sol`, `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol`)

---

### Summary

All L2 pool `deposit()` functions lack a `minRsETHAmount` parameter. The wrsETH/rsETH output is computed at execution time from a live oracle rate, so a user who simulates the transaction at one rate may receive materially fewer tokens if the oracle rate changes before the transaction is confirmed.

---

### Finding Description

Every L2 pool variant exposes two public `deposit()` overloads — one for native ETH and one for supported ERC-20 tokens. In each case the output amount is computed on-chain at execution time by calling `viewSwapRsETHAmountAndFee()`, which reads the live oracle rate via `getRate()`:

```
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;   // ETH path
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate; // token path
```

Neither overload accepts a `minRsETHAmount` argument, so there is no on-chain guard that reverts the transaction when the output falls below what the user expected.

This is in direct contrast to the mainnet `LRTDepositPool`, whose `depositETH()` and `depositAsset()` both accept `minRSETHAmountExpected` and enforce it inside `_beforeDeposit()`:

```solidity
if (rsethAmountToMint < minRSETHAmountExpected) {
    revert MinimumAmountToReceiveNotMet();
}
```

The affected entry points across all four L2 pool contracts are:

| Contract | Function |
|---|---|
| `RSETHPoolV3` | `deposit(string)` / `deposit(address,uint256,string)` |
| `RSETHPoolV3ExternalBridge` | `deposit(string)` / `deposit(address,uint256,string)` |
| `RSETHPoolNoWrapper` | `deposit(string)` / `deposit(address,uint256,string)` |
| `RSETHPoolV3WithNativeChainBridge` | `deposit(string)` / `deposit(address,uint256,string)` |

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but doesn't lose value.**

A user previews the exchange rate off-chain (e.g. via `viewSwapRsETHAmountAndFee`), decides to deposit, and submits the transaction. If the oracle rate increases before the transaction is mined (rsETH becomes more expensive in ETH terms), the user receives fewer wrsETH/rsETH tokens than expected with no on-chain protection. The deposited ETH/LST is not lost, but the user receives a worse-than-expected token count with no ability to revert.

---

### Likelihood Explanation

The rsETH/ETH rate is monotonically increasing over time as staking rewards accrue. On L2 networks, oracle updates may be batched or delayed, causing discrete rate jumps. Any deposit transaction that is pending in the mempool during such an update will silently execute at the new, less favorable rate. This is a routine, non-adversarial scenario requiring no attacker.

---

### Recommendation

Add a `minRsETHAmount` parameter to all four `deposit()` overloads in every L2 pool contract, mirroring the pattern already used in `LRTDepositPool._beforeDeposit()`:

```solidity
function deposit(string memory referralId, uint256 minRsETHAmount) external payable ... {
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmount) revert SlippageExceeded();
    ...
}
```

---

### Proof of Concept

**Mainnet `LRTDepositPool` — protected:**

`_beforeDeposit` enforces the minimum: [1](#0-0) 

**L2 `RSETHPoolV3.deposit(string)` — unprotected:**

No minimum check; output is silently determined by the live oracle rate at execution time: [2](#0-1) 

**L2 `RSETHPoolV3.deposit(address,uint256,string)` — unprotected:** [3](#0-2) 

**L2 `RSETHPoolV3ExternalBridge.deposit(string)` — unprotected:** [4](#0-3) 

**L2 `RSETHPoolNoWrapper.deposit(string)` — unprotected:** [5](#0-4) 

**L2 `RSETHPoolV3WithNativeChainBridge.deposit(string)` — unprotected:** [6](#0-5) 

**Rate computation that is read at execution time (no snapshot):** [7](#0-6)

### Citations

**File:** contracts/LRTDepositPool.sol (L665-669)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
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
