### Title
Integer Division Truncation in `viewSwapRsETHAmountAndFee` Silently Accepts Deposits While Minting Zero rsETH - (File: `contracts/pools/RSETHPoolNoWrapper.sol`, `contracts/pools/RSETHPoolV3.sol`, `contracts/pools/RSETHPoolV3ExternalBridge.sol`, `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol`)

---

### Summary

All L2 deposit pool variants share a `viewSwapRsETHAmountAndFee` function that computes the rsETH output via integer division. When a sufficiently small ETH or token amount is deposited, the division truncates to zero. The deposit function does not check whether `rsETHAmount == 0` before accepting the user's funds, so the user's ETH (or tokens) are taken by the pool while they receive nothing in return.

---

### Finding Description

Every L2 pool computes the rsETH output as:

**ETH path** (`RSETHPoolNoWrapper.sol`, `RSETHPoolV3.sol`, `RSETHPoolV3ExternalBridge.sol`, `RSETHPoolV3WithNativeChainBridge.sol`):

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**Token path** (same contracts):

```solidity
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

`rsETHToETHrate` is the oracle price of rsETH denominated in ETH, expressed in 18-decimal fixed-point. Because rsETH is a yield-bearing restaking token, its rate is always strictly greater than `1e18` (e.g., `1.05e18`).

For the ETH path, truncation to zero occurs whenever:

```
amountAfterFee * 1e18 < rsETHToETHrate
```

With `rsETHToETHrate = 1.05e18`, a deposit of `amountAfterFee = 1 wei` gives:

```
1 * 1e18 = 1e18 < 1.05e18  →  rsETHAmount = 0
```

The deposit functions only guard against `amount == 0`:

```solidity
if (amount == 0) revert InvalidAmount();
```

There is no guard against `rsETHAmount == 0`. The execution continues:

- **`RSETHPoolNoWrapper.sol`**: `rsETH.safeTransfer(msg.sender, 0)` — transfers zero rsETH; user's ETH is retained by the pool.
- **`RSETHPoolV3.sol` and variants**: `wrsETH.mint(msg.sender, 0)` — mints zero wrsETH; user's ETH is retained by the pool.

The retained ETH is eventually bridged to L1 as part of the pool's aggregate balance, with no per-user accounting or recovery path.

For the token path, the truncation threshold is higher when `tokenToETHRate < rsETHToETHrate`, meaning more than 1 wei of a lower-valued token can be silently consumed.

**Contrast with `LRTDepositPool`**: The L1 deposit pool is protected by both a `minAmountToDeposit` floor and a caller-supplied `minRSETHAmountExpected` slippage guard in `_beforeDeposit`. None of the L2 pool contracts implement either protection.

---

### Impact Explanation

A user who deposits a dust amount (e.g., 1 wei of ETH) receives 0 rsETH/wrsETH while their ETH is permanently absorbed into the pool. The protocol does not lose value — the ETH is still in the system — but the depositor loses their entire deposit with no recourse. This matches the **Low** impact category: *Contract fails to deliver promised returns, but doesn't lose value.*

---

### Likelihood Explanation

Any unprivileged external caller can trigger this by calling `deposit()` with a non-zero but sufficiently small `msg.value`. No special role, governance action, or front-running is required. The condition is deterministic and reproducible at any time the rsETH rate exceeds `1e18` (which is always true in normal operation). Likelihood is **Low** because the amounts involved are dust-level and accidental triggering is rare, but deliberate triggering is trivially easy.

---

### Recommendation

Add a zero-output guard in every `deposit` function (or inside `viewSwapRsETHAmountAndFee`) across all pool variants:

```solidity
if (rsETHAmount == 0) revert InvalidAmount();
```

Alternatively, enforce a minimum deposit floor analogous to `LRTDepositPool`'s `minAmountToDeposit`, or require callers to supply a `minRsETHAmountExpected` slippage parameter that is checked before accepting funds.

---

### Proof of Concept

Applies to `RSETHPoolNoWrapper.sol` (and identically to all other pool variants):

1. Deploy or use an existing `RSETHPoolNoWrapper` instance where `rsETHToETHrate > 1e18` (normal operating condition).
2. Call `deposit{value: 1}("")` — sending exactly 1 wei of ETH.
3. Inside `viewSwapRsETHAmountAndFee`:
   - `fee = 1 * feeBps / 10_000 = 0` (rounds to zero for 1 wei)
   - `amountAfterFee = 1`
   - `rsETHAmount = 1 * 1e18 / rsETHToETHrate = 1e18 / 1.05e18 = 0`
4. `rsETH.safeTransfer(msg.sender, 0)` executes without revert.
5. The caller's 1 wei is now held by the pool; the caller holds 0 additional rsETH.
6. The 1 wei will be included in the next `bridgeAssets` call and sent to L1 as undifferentiated pool ETH — permanently unrecoverable by the depositor.

Relevant code locations: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) 

Contrast with the protected L1 path: [9](#0-8)

### Citations

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L231-243)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L335-344)
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

**File:** contracts/LRTDepositPool.sol (L657-669)
```text
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
```
