### Title
Missing Default Fee Enforcement for Newly Added Tokens Allows Fee-Free Deposits - (File: contracts/pools/RSETHPool.sol)

### Summary
When a new ERC-20 token is registered in `RSETHPool` via `addSupportedToken`, the per-token fee mapping `tokenFeeBps[token]` is never initialized and silently defaults to 0. Any unprivileged depositor can immediately call `deposit(token, amount, referralId)` and receive rsETH at the full oracle rate with zero fee, depriving the protocol of its intended swap-fee revenue for the entire window between token registration and a subsequent admin call to `setTokenFeeBps`.

### Finding Description
`RSETHPool.addSupportedToken` sets `supportedTokenOracle[token]`, `tokenBridge[token]`, and pushes to `supportedTokenList`, but never touches `tokenFeeBps[token]`:

```solidity
// contracts/pools/RSETHPool.sol – addSupportedToken (lines 637-655)
supportedTokenList.push(token);
supportedTokenOracle[token] = oracle;
tokenBridge[token] = bridge;
// tokenFeeBps[token] is never set → defaults to 0
```

The public `deposit(address token, ...)` path calls `viewSwapRsETHAmountAndFee(amount, token)`, which reads `tokenFeeBps[token]` directly:

```solidity
// contracts/pools/RSETHPool.sol – viewSwapRsETHAmountAndFee (lines 335-346)
uint256 feeBpsForToken = tokenFeeBps[token];   // 0 for any new token
fee = amount * feeBpsForToken / 10_000;         // fee == 0
uint256 amountAfterFee = amount - fee;          // full amount passes through
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

There is no guard that checks whether a fee has been explicitly configured before allowing deposits. The protocol's intent to charge fees on all token deposits (evidenced by the `feeBps` variable for ETH deposits and the `tokenFeeBps` mapping for ERC-20 deposits) is silently absent for every newly added token.

This is the direct analog of the external report: just as `optional_royalty_pct` is consumed without verifying whether the token standard mandates a specific royalty, here `tokenFeeBps[token]` is consumed without verifying whether a fee has been configured — and the protocol-enforced fee is absent.

### Impact Explanation
The protocol loses all swap-fee revenue on deposits of the newly added token for the duration of the zero-fee window. `feeEarnedInToken[token]` remains 0; the BRIDGER_ROLE collects nothing. Depositors receive rsETH at the full oracle-rate conversion, extracting value that the protocol is designed to retain as fee yield. This is **theft of unclaimed yield** (High).

### Likelihood Explanation
Low-to-Medium. The condition is triggered every time a new token is added via `addSupportedToken` (a `TIMELOCK_ROLE` action). The window persists until a separate `setTokenFeeBps` call is made. Any user monitoring the `AddSupportedToken` event — or watching the mempool — can immediately deposit at 0 fee with no special privileges. No oracle manipulation, governance capture, or key compromise is required.

### Recommendation
Add a `_feeBps` parameter to `addSupportedToken` and set `tokenFeeBps[token] = _feeBps` atomically during registration, applying the same `_feeBps > 10_000 → revert InvalidFeeAmount()` guard already present in `setTokenFeeBps`. This eliminates the zero-fee window entirely.

### Proof of Concept
1. Admin calls `addSupportedToken(tokenX, oracleX, bridgeX)` — `tokenFeeBps[tokenX]` is `0`.
2. Attacker calls `deposit(tokenX, 1_000e18, "ref")` in the same or next block.
3. `viewSwapRsETHAmountAndFee(1_000e18, tokenX)` computes `fee = 1_000e18 * 0 / 10_000 = 0`.
4. Attacker receives `rsETHAmount = 1_000e18 * tokenToETHRate / rsETHToETHrate` — the full oracle-rate amount with no fee deducted.
5. `feeEarnedInToken[tokenX]` remains `0`; the protocol collects nothing.
6. Admin later calls `setTokenFeeBps(tokenX, 30)` — but all deposits made before this call were fee-free. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** contracts/pools/RSETHPool.sol (L637-655)
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
```
