### Title
`addSupportedToken` Does Not Initialize `tokenFeeBps`, Allowing Fee-Free Token Deposits - (File: contracts/pools/RSETHPool.sol)

### Summary
`RSETHPool.sol` maintains a per-token fee mapping `tokenFeeBps` that defaults to `0` for every newly added token. When the admin calls `addSupportedToken`, no fee is set for that token. Any depositor who calls `deposit(token, amount, referralId)` before the admin separately calls `setTokenFeeBps` pays zero protocol fees, permanently losing that fee revenue for the protocol.

### Finding Description
`RSETHPool.sol` declares a per-token fee mapping:

```solidity
mapping(address token => uint256 feeBps) public tokenFeeBps;
``` [1](#0-0) 

When a new token is added via `addSupportedToken`, only the oracle and bridge are stored. `tokenFeeBps[token]` is never initialized and remains `0`:

```solidity
function addSupportedToken(address token, address oracle, address bridge) external onlyRole(TIMELOCK_ROLE) {
    ...
    supportedTokenList.push(token);
    supportedTokenOracle[token] = oracle;
    tokenBridge[token] = bridge;
    emit AddSupportedToken(token, oracle, bridge);
}
``` [2](#0-1) 

The fee computation for token deposits reads directly from this uninitialized mapping:

```solidity
uint256 feeBpsForToken = tokenFeeBps[token];
fee = amount * feeBpsForToken / 10_000;
``` [3](#0-2) 

Setting the fee requires a completely separate admin call to `setTokenFeeBps`:

```solidity
function setTokenFeeBps(address token, uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) onlySupportedToken(token) {
    if (_feeBps > 10_000) revert InvalidFeeAmount();
    tokenFeeBps[token] = _feeBps;
    emit TokenFeeBpsSet(token, _feeBps);
}
``` [4](#0-3) 

There is no enforcement that `setTokenFeeBps` must be called before or atomically with `addSupportedToken`. The token deposit path is immediately open to any caller once `addSupportedToken` succeeds.

### Impact Explanation
Every token deposit made while `tokenFeeBps[token] == 0` charges zero fee. The depositor receives rsETH computed on the full `amount` (no deduction), and `feeEarnedInToken[token]` accumulates nothing. Protocol fee revenue for that token is permanently lost for all deposits in this window. This maps to **High — Theft of unclaimed yield**.

### Likelihood Explanation
`addSupportedToken` is gated by `TIMELOCK_ROLE`, meaning it goes through a timelock delay and is publicly visible on-chain before execution. Any observer can front-run or simply deposit immediately after the timelock executes `addSupportedToken` and before the admin submits a separate `setTokenFeeBps` transaction. Even without front-running, the two-step configuration creates a guaranteed fee-free window. Likelihood is **Medium**.

### Recommendation
Pass the initial `feeBps` as a parameter to `addSupportedToken` and set it atomically:

```solidity
function addSupportedToken(address token, address oracle, address bridge, uint256 _feeBps)
    external onlyRole(TIMELOCK_ROLE)
{
    ...
    tokenFeeBps[token] = _feeBps;
    ...
}
```

Alternatively, gate `deposit(token, ...)` with a check that `tokenFeeBps[token]` has been explicitly configured (e.g., require a sentinel value distinct from 0, or a separate `isTokenFeeSet` flag).

### Proof of Concept
1. Admin calls `addSupportedToken(wstETH, oracle, bridge)` — `tokenFeeBps[wstETH]` is `0`.
2. Depositor immediately calls `deposit(wstETH, 100 ether, "ref")`.
3. `viewSwapRsETHAmountAndFee(100 ether, wstETH)` computes `fee = 100 ether * 0 / 10_000 = 0`.
4. Depositor receives rsETH for the full `100 ether` with no fee deducted; `feeEarnedInToken[wstETH]` remains `0`.
5. Admin later calls `setTokenFeeBps(wstETH, 30)` — but the fee revenue from step 2–4 is permanently lost. [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/pools/RSETHPool.sol (L87-88)
```text
    /// @dev Mapping of token to fee basis points
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
