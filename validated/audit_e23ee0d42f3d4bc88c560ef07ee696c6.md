### Title
Token Deposit Fee Bypass via Uninitialized `tokenFeeBps` Mapping - (File: contracts/pools/RSETHPool.sol)

### Summary

`RSETHPool.viewSwapRsETHAmountAndFee(uint256 amount, address token)` reads `tokenFeeBps[token]` from a storage mapping that is never initialized when a token is added via `addSupportedToken`. Because Solidity mappings default to `0`, every token deposit computes `fee = 0`, allowing any depositor to bypass protocol fees entirely on all ERC-20 token deposits.

### Finding Description

`RSETHPool` (the Arbitrum pool) maintains two separate fee variables:

- `feeBps` — used for ETH deposits, set during `initialize()`
- `tokenFeeBps` — a per-token mapping used for ERC-20 token deposits, **never set during `addSupportedToken()`** [1](#0-0) 

When a token is added: [2](#0-1) 

`tokenFeeBps[token]` is never written. It remains `0`.

When a user calls `deposit(token, amount, referralId)`, the fee is computed as: [3](#0-2) 

With `feeBpsForToken == 0`, `fee` is always `0`. The `feeEarnedInToken[token]` accumulator never grows: [4](#0-3) 

The depositor receives the full rsETH amount with no fee deducted, and the protocol treasury receives nothing.

This is structurally identical to the Burve bug: a value that should be non-zero is zero at the point of fee calculation, causing 100% fee bypass. In Burve the cause was a return variable read before assignment; here the cause is a storage mapping that defaults to zero because `addSupportedToken` never initializes it.

### Impact Explanation

**High — Theft of unclaimed yield (protocol fees).**

Every ERC-20 token deposit to `RSETHPool` (Arbitrum) pays zero protocol fees. The `feeEarnedInToken[token]` balance that `withdrawFees(receiver, token)` would distribute to the protocol treasury is permanently zero. All fee revenue on token deposits is lost to the protocol for as long as `tokenFeeBps[token]` remains unset.

### Likelihood Explanation

**High.** The entry path is the public `deposit(address token, uint256 amount, string referralId)` function, callable by any unprivileged user with no preconditions beyond holding a supported token. No admin compromise, front-running, or special setup is required. The condition (uninitialized `tokenFeeBps`) holds for every token from the moment it is added until an admin explicitly calls `setTokenFeeBps`, and there is no enforcement that this call must happen before deposits are accepted. [5](#0-4) 

### Recommendation

Initialize `tokenFeeBps[token]` inside `addSupportedToken` (or require an explicit fee parameter), and/or add a check in `viewSwapRsETHAmountAndFee` that reverts if `tokenFeeBps[token]` has not been set:

```diff
function addSupportedToken(
    address token,
    address oracle,
-   address bridge
+   address bridge,
+   uint256 _feeBps
) external onlyRole(TIMELOCK_ROLE) {
    ...
+   if (_feeBps > 10_000) revert InvalidFeeAmount();
+   tokenFeeBps[token] = _feeBps;
    emit AddSupportedToken(token, oracle, bridge);
}
```

### Proof of Concept

1. Admin calls `addSupportedToken(wstETH, oracle, bridge)` — `tokenFeeBps[wstETH]` is `0`.
2. User calls `deposit(wstETH, 10 ether, "ref")`.
3. `viewSwapRsETHAmountAndFee(10 ether, wstETH)` executes:
   - `feeBpsForToken = tokenFeeBps[wstETH]` → `0`
   - `fee = 10 ether * 0 / 10_000` → `0`
   - `amountAfterFee = 10 ether`
4. `feeEarnedInToken[wstETH] += 0` — treasury receives nothing.
5. User receives rsETH equivalent to the full `10 ether` with zero fee deducted.
6. Repeat for every token deposit; protocol collects `0` in token fees indefinitely. [6](#0-5)

### Citations

**File:** contracts/pools/RSETHPool.sol (L88-88)
```text
    mapping(address token => uint256 feeBps) public tokenFeeBps;
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

**File:** contracts/pools/RSETHPool.sol (L637-656)
```text
    function addSupportedToken(address token, address oracle, address bridge) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(token);
        UtilLib.checkNonZeroAddress(oracle);
        UtilLib.checkNonZeroAddress(bridge);

        if (supportedTokenOracle[token] != address(0)) {
            revert AlreadySupportedToken();
        }
        if (tokenBridge[token] != address(0)) {
            revert AlreadySupportedToken();
        }
        if (IOracle(oracle).getRate() == 0) {
            revert UnsupportedOracle();
        }
        supportedTokenList.push(token);
        supportedTokenOracle[token] = oracle;
        tokenBridge[token] = bridge;

        emit AddSupportedToken(token, oracle, bridge);
    }
```
