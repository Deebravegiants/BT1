### Title
Tokens Minted Exclusively to `msg.sender` with No Recipient Override, Causing Permanent Fund Freeze for Contract Callers - (File: contracts/pools/RSETHPoolV3ExternalBridge.sol)

---

### Summary

Every `deposit()` variant across all L2 pool contracts mints or transfers wrsETH/rsETH unconditionally to `msg.sender`, with no `depositTo(address recipient, ...)` override. When a smart contract (e.g., a DeFi aggregator, vault, or router) calls `deposit()` on behalf of an end user, the minted tokens land at the calling contract's own address. If that contract has no logic to forward or recover ERC-20 tokens it did not expect to hold, the deposited value is permanently frozen.

---

### Finding Description

All four production pool contracts share the same pattern. In `RSETHPoolV3ExternalBridge.sol`:

```solidity
// ETH deposit
wrsETH.mint(msg.sender, rsETHAmount);          // line 381

// Token deposit
wrsETH.mint(msg.sender, rsETHAmount);          // line 409
```

The same pattern appears in `RSETHPoolV3.sol` (lines 262, 290), `RSETHPool.sol` (lines 275, 302), and `RSETHPoolNoWrapper.sol` (lines 241, 268). None of these contracts expose a `depositTo(address _to, ...)` variant that would let the caller specify a beneficiary address distinct from itself.

The analog to the reported ZKSync bug is direct: in that bug, `msg.sender` was used as the default refund recipient when a contract initiated a cross-chain transaction, and the contract could not control that address on L2. Here, `msg.sender` is used as the sole mint recipient when a contract initiates a deposit, and if the contract has no mechanism to forward or rescue the minted ERC-20 tokens, those tokens are permanently inaccessible to the intended end user.

---

### Impact Explanation

**Permanent freezing of funds (Critical).**

A contract caller (aggregator, vault, router, or any smart-contract wallet that does not implement ERC-20 rescue logic) deposits ETH or a supported LST into the pool. The pool mints wrsETH to the contract's own address. Because the contract never anticipated holding wrsETH and has no `transfer`, `sweep`, or rescue path for it, the tokens are irrecoverably locked at that address. The depositor's ETH or LST has already been consumed by the pool; the wrsETH representing that value is unreachable.

---

### Likelihood Explanation

**Medium.**

DeFi composability is a primary use case for L2 liquidity pools. Aggregators (e.g., 1inch, Paraswap, Li.Fi), yield vaults, and smart-contract wallets routinely call pool `deposit()` functions on behalf of users. Many such contracts are minimal proxies or purpose-built routers that hold no ERC-20 rescue logic. The absence of a `depositTo()` path means every such integration silently routes minted tokens to the wrong address. No special permissions are required; any unprivileged contract caller triggers the condition.

---

### Recommendation

Add a `depositTo(address _recipient, ...)` overload (or an optional `_recipient` parameter) to every `deposit()` function across all pool variants. Mint/transfer the output tokens to `_recipient` instead of `msg.sender`. If `_recipient` is `address(0)`, default to `msg.sender` to preserve backward compatibility with EOA callers. This mirrors the fix applied in the referenced ZKSync PR #32, which disallowed unspecified recipients for ETH transfers and reverted when the sender was not an EOA.

---

### Proof of Concept

1. Deploy a minimal aggregator contract `Aggregator` that:
   - Accepts ETH from a user.
   - Calls `RSETHPoolV3ExternalBridge.deposit{value: amount}("ref")`.
   - Has no `transfer` or rescue function for wrsETH.

2. User sends 1 ETH to `Aggregator`, which forwards it to the pool.

3. Pool executes `wrsETH.mint(msg.sender, rsETHAmount)` where `msg.sender == address(Aggregator)`.

4. `wrsETH.balanceOf(address(Aggregator)) > 0`; `wrsETH.balanceOf(user) == 0`.

5. No function on `Aggregator` can move the wrsETH. The user's 1 ETH is permanently converted into wrsETH that neither the user nor the aggregator can access.

Affected lines: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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
