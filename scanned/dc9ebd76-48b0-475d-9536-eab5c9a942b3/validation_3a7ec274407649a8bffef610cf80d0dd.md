### Title
`RSETHPool` Token Deposits Collect Zero Protocol Fees Due to Uninitialized `tokenFeeBps` - (File: contracts/pools/RSETHPool.sol)

### Summary

`RSETHPool.sol` (the Arbitrum L2 pool) uses a per-token fee mapping `tokenFeeBps[token]` for ERC-20 token deposits, which defaults to `0` for every token added via `addSupportedToken()`. The existence of `setTokenFeeBps()` signals that non-zero per-token fees were intended, but because `addSupportedToken()` never initialises `tokenFeeBps[token]`, all token deposits (e.g. wstETH on Arbitrum) permanently collect zero protocol fees unless an admin separately calls `setTokenFeeBps`. This is the direct analog of the IndexPool bug: a fee setter function exists, implying fee collection was intended, but the structural default means fees are never actually accrued.

### Finding Description

`RSETHPool.sol` maintains two separate fee variables:

- `feeBps` — a global basis-point fee applied to native ETH deposits, set at `initialize()` time.
- `tokenFeeBps[token]` — a per-token basis-point fee applied to ERC-20 deposits, **never set** when a token is added. [1](#0-0) [2](#0-1) 

The token deposit path computes the fee exclusively from `tokenFeeBps[token]`:

```solidity
uint256 feeBpsForToken = tokenFeeBps[token];
fee = amount * feeBpsForToken / 10_000;
``` [3](#0-2) 

Because `tokenFeeBps[token]` is a mapping that Solidity zero-initialises, every token added through `addSupportedToken()` has an effective fee of `0`. The `setTokenFeeBps()` admin function exists to correct this: [4](#0-3) 

But `addSupportedToken()` never calls it, so the default state is zero fees for all token deposits. Compare this with ETH deposits, which correctly use the non-zero `feeBps`: [5](#0-4) 

The token deposit function accumulates `feeEarnedInToken[token] += fee`, but since `fee == 0`, nothing is ever accrued: [6](#0-5) 

All other pool variants (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPoolNoWrapper`) use a single global `feeBps` for both ETH and token deposits and do not have this split. `RSETHPool.sol` is the only contract with the divergent `tokenFeeBps` design. [7](#0-6) 

### Impact Explanation

**High — Theft of unclaimed yield.**

The protocol is structurally entitled to fee revenue from every token deposit on Arbitrum. Because `tokenFeeBps[token]` is never initialised, 100% of the fee revenue from token deposits (wstETH, and any future supported tokens) is permanently foregone. The `withdrawFees(receiver, token)` function will always transfer `0` tokens regardless of deposit volume. [8](#0-7) 

This is not a temporary misconfiguration — it is the structural default state of the contract. Every token deposit since deployment has paid zero fees.

### Likelihood Explanation

**High.** The condition is always true: `tokenFeeBps[token]` is `0` for every token unless an admin has explicitly called `setTokenFeeBps` after the fact. Any user calling `deposit(token, amount, referralId)` on `RSETHPool.sol` triggers the zero-fee path. No special conditions, timing, or attacker capability is required — ordinary depositors exercise this path on every transaction. [9](#0-8) 

### Recommendation

Modify `addSupportedToken()` to accept a `_feeBps` parameter and set `tokenFeeBps[token] = _feeBps` at token registration time, mirroring how `feeBps` is set at `initialize()`. Alternatively, fall back to the global `feeBps` when `tokenFeeBps[token]` is zero, consistent with the behaviour of all other pool variants.

### Proof of Concept

1. Admin calls `addSupportedToken(wstETH, oracle, bridge)` on `RSETHPool.sol`. `tokenFeeBps[wstETH]` is `0` (never set).
2. User calls `deposit(wstETH, 10 ether, "ref")`.
3. `viewSwapRsETHAmountAndFee(10 ether, wstETH)` executes: `feeBpsForToken = tokenFeeBps[wstETH] = 0`, so `fee = 10 ether * 0 / 10_000 = 0`.
4. `feeEarnedInToken[wstETH] += 0` — no fee accrued.
5. User receives the full `rsETHAmount` computed on the entire `10 ether` with zero fee deducted.
6. Admin calls `withdrawFees(receiver, wstETH)` — transfers `0` tokens regardless of total deposit volume. [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/pools/RSETHPool.sol (L43-44)
```text
    uint256 public feeBps; // Basis points for fees for ETH deposits
    uint256 public feeEarnedInETH;
```

**File:** contracts/pools/RSETHPool.sol (L87-88)
```text
    /// @dev Mapping of token to fee basis points
    mapping(address token => uint256 feeBps) public tokenFeeBps;
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

**File:** contracts/pools/RSETHPool.sol (L284-305)
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
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
    }
```

**File:** contracts/pools/RSETHPool.sol (L335-337)
```text
        uint256 feeBpsForToken = tokenFeeBps[token];
        fee = amount * feeBpsForToken / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/pools/RSETHPool.sol (L427-443)
```text
    /// @dev Withdraws fees earned by the pool
    function withdrawFees(
        address receiver,
        address token
    )
        external
        nonReentrant
        onlySupportedToken(token)
        onlyRole(BRIDGER_ROLE)
    {
        // withdraw fees in ETH
        uint256 amountToSendInToken = feeEarnedInToken[token];
        feeEarnedInToken[token] = 0;
        IERC20(token).safeTransfer(receiver, amountToSendInToken);

        emit FeesWithdrawn(amountToSendInToken, token);
    }
```

**File:** contracts/pools/RSETHPool.sol (L583-594)
```text
    function setTokenFeeBps(
        address token,
        uint256 _feeBps
    )
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
        onlySupportedToken(token)
    {
        if (_feeBps > 10_000) revert InvalidFeeAmount();
        tokenFeeBps[token] = _feeBps;
        emit TokenFeeBpsSet(token, _feeBps);
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L286-292)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
```
