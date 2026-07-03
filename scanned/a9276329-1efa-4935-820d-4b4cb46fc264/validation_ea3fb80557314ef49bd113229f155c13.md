### Title
Uninitialized `tokenFeeBps` for Newly Added Tokens Allows Fee-Free Deposits - (File: `contracts/pools/RSETHPool.sol`)

### Summary
When a new token is added via `addSupportedToken`, the `tokenFeeBps[token]` mapping entry is never initialized, defaulting to 0. Any user can deposit that token and receive rsETH without paying any protocol fee until an admin separately calls `setTokenFeeBps`. This is a direct analog to the reported "uninitialized field" class: a missing initialization of a calculation-critical field causes incorrect financial output (zero fee instead of the intended fee).

### Finding Description
`RSETHPool.addSupportedToken` sets `supportedTokenOracle[token]` and `tokenBridge[token]` but never initializes `tokenFeeBps[token]`:

```solidity
// contracts/pools/RSETHPool.sol
function addSupportedToken(address token, address oracle, address bridge) external onlyRole(TIMELOCK_ROLE) {
    ...
    supportedTokenList.push(token);
    supportedTokenOracle[token] = oracle;
    tokenBridge[token] = bridge;          // tokenFeeBps[token] is never set here
    emit AddSupportedToken(token, oracle, bridge);
}
``` [1](#0-0) 

Because Solidity mappings default to zero, `tokenFeeBps[token]` is `0` for every newly added token. The fee calculation in `viewSwapRsETHAmountAndFee(uint256, address)` then computes:

```solidity
uint256 feeBpsForToken = tokenFeeBps[token];   // == 0
fee = amount * feeBpsForToken / 10_000;         // == 0
uint256 amountAfterFee = amount - fee;          // == amount (no fee deducted)
``` [2](#0-1) 

The `deposit(address token, uint256 amount, string referralId)` function calls this view function and mints rsETH based on the fee-free amount:

```solidity
function deposit(address token, uint256 amount, string memory referralId)
    external nonReentrant whenNotPaused onlySupportedToken(token)
{
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
    feeEarnedInToken[token] += fee;                          // += 0
    IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);
    ...
}
``` [3](#0-2) 

The `setTokenFeeBps` function is a separate, independent admin call with no coupling to `addSupportedToken`:

```solidity
function setTokenFeeBps(address token, uint256 _feeBps)
    external onlyRole(DEFAULT_ADMIN_ROLE) onlySupportedToken(token)
{
    if (_feeBps > 10_000) revert InvalidFeeAmount();
    tokenFeeBps[token] = _feeBps;
    emit TokenFeeBpsSet(token, _feeBps);
}
``` [4](#0-3) 

There is no atomicity guarantee between `addSupportedToken` and `setTokenFeeBps`. The window between these two transactions — which may span multiple blocks — is exploitable by any depositor.

### Impact Explanation
**High — Theft of unclaimed yield (protocol fees).** During the window between `addSupportedToken` and `setTokenFeeBps`, every token deposit pays zero fee. An attacker monitoring the mempool can front-run or simply race the `setTokenFeeBps` call to deposit a large token amount and receive rsETH at a 0% fee rate, permanently depriving the protocol of the fee revenue that would have accrued on those deposits. The `feeEarnedInToken[token]` accumulator records `0` for these deposits, so the loss is permanent and unrecoverable.

### Likelihood Explanation
**Medium.** Adding a new supported token is a routine protocol operation. The two-step pattern (`addSupportedToken` then `setTokenFeeBps`) is structurally required by the current code, making the zero-fee window unavoidable on every new token addition. A sophisticated depositor watching on-chain events for `AddSupportedToken` can immediately exploit the window before the fee is set.

### Recommendation
Add a `feeBps` parameter directly to `addSupportedToken` and initialize `tokenFeeBps[token]` atomically in the same call:

```solidity
function addSupportedToken(
    address token,
    address oracle,
    address bridge,
    uint256 feeBps          // <-- add this
) external onlyRole(TIMELOCK_ROLE) {
    ...
    if (feeBps > 10_000) revert InvalidFeeAmount();
    supportedTokenList.push(token);
    supportedTokenOracle[token] = oracle;
    tokenBridge[token] = bridge;
    tokenFeeBps[token] = feeBps;           // <-- initialize atomically
    emit AddSupportedToken(token, oracle, bridge);
}
```

### Proof of Concept
1. TIMELOCK_ROLE submits `addSupportedToken(wstETH, oracle, bridge)` — `tokenFeeBps[wstETH]` is `0`.
2. Attacker observes the `AddSupportedToken` event (or the pending tx) and immediately calls `deposit(wstETH, 1_000e18, "")`.
3. `viewSwapRsETHAmountAndFee(1_000e18, wstETH)` computes `fee = 1_000e18 * 0 / 10_000 = 0`; attacker receives the full rsETH equivalent of 1,000 wstETH with no fee deducted.
4. Admin later calls `setTokenFeeBps(wstETH, 50)` (0.5% fee), but the attacker's deposit has already settled at 0% — the protocol permanently lost ~5 wstETH worth of fees on that single deposit.
5. This can be repeated by any depositor for every new token addition until `setTokenFeeBps` is confirmed on-chain.

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

**File:** contracts/pools/RSETHPool.sol (L335-347)
```text
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
