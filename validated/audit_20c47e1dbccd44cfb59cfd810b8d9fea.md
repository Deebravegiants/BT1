### Title
Zero `tokenFeeBps` on Newly Added Tokens Allows Fee-Free Deposits - (`contracts/pools/RSETHPool.sol`)

### Summary

`RSETHPool.addSupportedToken` does not atomically set `tokenFeeBps[token]`, leaving it at the Solidity default of `0`. Any depositor can call `deposit(token, amount, referralId)` immediately after the token is added and receive the full rsETH amount with zero fee charged, until a separate `setTokenFeeBps` call is made by the admin.

### Finding Description

`RSETHPool` maintains a per-token fee mapping:

```solidity
mapping(address token => uint256 feeBps) public tokenFeeBps;
``` [1](#0-0) 

When a new token is added via `addSupportedToken`, the function sets the oracle and bridge but **never initialises `tokenFeeBps[token]`**:

```solidity
function addSupportedToken(address token, address oracle, address bridge) external onlyRole(TIMELOCK_ROLE) {
    ...
    supportedTokenList.push(token);
    supportedTokenOracle[token] = oracle;
    tokenBridge[token] = bridge;
    // tokenFeeBps[token] is never set → defaults to 0
    emit AddSupportedToken(token, oracle, bridge);
}
``` [2](#0-1) 

The fee is set in a completely separate, optional call:

```solidity
function setTokenFeeBps(address token, uint256 _feeBps) external onlyRole(DEFAULT_ADMIN_ROLE) onlySupportedToken(token) {
    tokenFeeBps[token] = _feeBps;
}
``` [3](#0-2) 

During the window between `addSupportedToken` and `setTokenFeeBps`, every token deposit goes through:

```solidity
uint256 feeBpsForToken = tokenFeeBps[token]; // == 0
fee = amount * feeBpsForToken / 10_000;      // == 0
uint256 amountAfterFee = amount - fee;        // == amount (full amount)
``` [4](#0-3) 

The depositor receives rsETH calculated on the full `amount` with no fee deducted and no fee accrued to `feeEarnedInToken[token]`.

### Impact Explanation

Every token deposit made between `addSupportedToken` and `setTokenFeeBps` pays zero protocol fee. The fee revenue that should have accrued to `feeEarnedInToken[token]` (and ultimately to the protocol via `withdrawFees`) is permanently lost. This is **theft of unclaimed yield** — the protocol fails to collect fees it is entitled to, and depositors receive more rsETH than they should.

### Likelihood Explanation

The trigger is a normal, expected admin operation (`addSupportedToken`). Because `TIMELOCK_ROLE` is involved, the token addition is likely announced or observable on-chain before execution. Any depositor — including a bot watching the mempool — can front-run or immediately follow the `addSupportedToken` transaction with a large `deposit(token, ...)` call. The window persists until the admin separately calls `setTokenFeeBps`, which may span multiple blocks or even be forgotten entirely. This can happen on every new token addition.

### Recommendation

Pass the initial fee basis points as a parameter to `addSupportedToken` and set it atomically:

```solidity
function addSupportedToken(address token, address oracle, address bridge, uint256 _feeBps)
    external onlyRole(TIMELOCK_ROLE)
{
    ...
    if (_feeBps > 10_000) revert InvalidFeeAmount();
    supportedTokenList.push(token);
    supportedTokenOracle[token] = oracle;
    tokenBridge[token] = bridge;
    tokenFeeBps[token] = _feeBps;          // set atomically
    emit AddSupportedToken(token, oracle, bridge);
    emit TokenFeeBpsSet(token, _feeBps);
}
```

### Proof of Concept

1. Admin calls `addSupportedToken(wstETH, wstETHOracle, wstETHBridge)` — `tokenFeeBps[wstETH]` is `0`.
2. Attacker (or any user) immediately calls `deposit(wstETH, 1_000e18, "")`.
3. `viewSwapRsETHAmountAndFee(1_000e18, wstETH)` computes `fee = 1_000e18 * 0 / 10_000 = 0`.
4. `feeEarnedInToken[wstETH]` remains `0`; attacker receives rsETH for the full `1_000e18` with no fee.
5. Admin later calls `setTokenFeeBps(wstETH, 30)` — but the fee on the attacker's deposit is already lost.
6. This is repeatable on every new token addition and can be executed at any scale. [5](#0-4) [6](#0-5)

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
