### Title
Token Deposits in `RSETHPool` Bypass Protocol Fee Due to Uninitialized `tokenFeeBps` — (File: contracts/pools/RSETHPool.sol)

---

### Summary

`RSETHPool.sol` (Arbitrum) charges fees on ETH deposits using the global `feeBps`, but charges fees on token deposits using a per-token `tokenFeeBps[token]` mapping that is **never initialized** when a token is added via `addSupportedToken`. Because Solidity mappings default to zero, every token deposit pays zero fee, while ETH deposits pay the intended rate. The protocol silently loses all fee revenue from token deposits.

---

### Finding Description

`RSETHPool.viewSwapRsETHAmountAndFee(uint256 amount, address token)` computes the fee as:

```solidity
uint256 feeBpsForToken = tokenFeeBps[token];   // always 0 unless explicitly set
fee = amount * feeBpsForToken / 10_000;         // always 0
``` [1](#0-0) 

`addSupportedToken` registers the oracle and bridge for a token but never writes to `tokenFeeBps`:

```solidity
supportedTokenList.push(token);
supportedTokenOracle[token] = oracle;
tokenBridge[token] = bridge;
// tokenFeeBps[token] is never set → remains 0
``` [2](#0-1) 

The ETH deposit path, by contrast, correctly uses the global `feeBps`:

```solidity
fee = amount * feeBps / 10_000;
``` [3](#0-2) 

The inconsistency is confirmed by comparing with `RSETHPoolV3.sol`, which applies the global `feeBps` uniformly to both ETH and token deposits:

```solidity
fee = amount * feeBps / 10_000;   // same variable for all assets
``` [4](#0-3) 

`setTokenFeeBps` exists as a separate admin call, but it is never invoked inside `addSupportedToken`, so the window between token addition and a manual `setTokenFeeBps` call (or indefinitely if the call is omitted) leaves the fee at zero. [5](#0-4) 

---

### Impact Explanation

Every token deposit (e.g., wstETH) through `RSETHPool.deposit(token, amount, referralId)` on Arbitrum pays **zero protocol fee** instead of the intended `feeBps` rate. The fee revenue that should accrue to the protocol treasury is permanently lost for every such deposit. This maps to **High — theft of unclaimed yield**: yield (fee revenue) that the protocol is entitled to collect is never collected. [6](#0-5) 

---

### Likelihood Explanation

The entry path is fully permissionless — any user can call `deposit(token, amount, referralId)` on the live Arbitrum `RSETHPool` contract. No special role, front-running, or external condition is required. The condition holds for every token whose `tokenFeeBps` has not been explicitly set after `addSupportedToken`, which is the default state.

---

### Recommendation

Initialize `tokenFeeBps[token]` to the global `feeBps` inside `addSupportedToken`, or replace the per-token lookup with the global `feeBps` in `viewSwapRsETHAmountAndFee(amount, token)` to match the behaviour of `RSETHPoolV3`:

```solidity
// Option A – use global feeBps as default
fee = amount * feeBps / 10_000;

// Option B – initialize on token addition
tokenFeeBps[token] = feeBps;
```

---

### Proof of Concept

1. Admin calls `addSupportedToken(wstETH, oracle, bridge)` — `tokenFeeBps[wstETH]` remains `0`.
2. User calls `deposit(wstETH, 10 ether, "ref")`.
3. `viewSwapRsETHAmountAndFee(10 ether, wstETH)` returns `fee = 0`, `rsETHAmount = 10 ether * tokenToETHRate / rsETHToETHrate` (full amount, no deduction).
4. `feeEarnedInToken[wstETH] += 0` — protocol collects nothing.
5. User receives the same rsETH amount as if `feeBps` were zero, while an ETH depositor of equivalent value would pay `feeBps` basis points. [7](#0-6)

### Citations

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

**File:** contracts/pools/RSETHPool.sol (L312-312)
```text
        fee = amount * feeBps / 10_000;
```

**File:** contracts/pools/RSETHPool.sol (L326-347)
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
        uint256 feeBpsForToken = tokenFeeBps[token];
        fee = amount * feeBpsForToken / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
    }
```

**File:** contracts/pools/RSETHPool.sol (L583-593)
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

**File:** contracts/pools/RSETHPoolV3.sol (L324-324)
```text
        fee = amount * feeBps / 10_000;
```
