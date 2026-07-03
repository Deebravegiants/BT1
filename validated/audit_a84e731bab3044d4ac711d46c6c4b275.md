### Title
Token Deposits in RSETHPool Bypass Protocol Fees Due to Uninitialized `tokenFeeBps` - (File: contracts/pools/RSETHPool.sol)

### Summary
`RSETHPool.sol` (the Arbitrum pool) introduced a per-token fee mapping `tokenFeeBps` for ERC-20 token deposits, separate from the ETH deposit fee `feeBps`. Because `tokenFeeBps[token]` defaults to `0` in Solidity and `addSupportedToken` never initializes it, all token deposits incur zero protocol fees. Any user can deposit supported tokens (e.g., wstETH) and receive rsETH at the full exchange rate with no fee deducted, while ETH depositors pay the configured `feeBps`.

### Finding Description
`RSETHPool.sol` maintains two distinct fee variables:

- `feeBps` — used for native ETH deposits, set at initialization.
- `tokenFeeBps[token]` — used for ERC-20 token deposits, introduced as a new storage variable.

The ETH deposit path: [1](#0-0) 

The token deposit path uses `tokenFeeBps[token]`: [2](#0-1) 

`addSupportedToken` registers a token with an oracle and bridge, but never sets `tokenFeeBps`: [3](#0-2) 

`setTokenFeeBps` is a separate admin call that must be invoked explicitly: [4](#0-3) 

Because `tokenFeeBps[token]` is never initialized in `addSupportedToken`, it remains `0` for every supported token unless the admin separately calls `setTokenFeeBps`. This means `fee = amount * 0 / 10_000 = 0` for all token deposits, and `feeEarnedInToken[token]` never accumulates any value. [5](#0-4) 

### Impact Explanation
Protocol fee revenue on token deposits is permanently zero until an admin explicitly calls `setTokenFeeBps`. Any user depositing a supported token (e.g., wstETH) receives the full rsETH amount at the oracle rate with no fee deducted. This is a direct loss of protocol fee yield — the same class of impact as M-12 where a secondary swap path bypassed fee collection. Impact: **High — Theft of unclaimed yield** (protocol fee revenue that should accrue to the treasury is silently lost on every token deposit).

### Likelihood Explanation
The entry path is fully permissionless: any user can call `deposit(token, amount, referralId)` on the live Arbitrum `RSETHPool` contract at any time the contract is not paused. No special role or condition is required. The fee bypass is structural — it applies to every token deposit until `setTokenFeeBps` is explicitly called per token. Given that `addSupportedToken` gives no indication that a follow-up `setTokenFeeBps` call is required, this is likely to persist unnoticed. Likelihood: **High**.

### Recommendation
Initialize `tokenFeeBps[token]` inside `addSupportedToken` (or require it as a parameter), so that every newly added token inherits a non-zero fee from the moment it is registered. Alternatively, fall back to `feeBps` when `tokenFeeBps[token]` is zero, mirroring the behavior of all other pool contracts.

```solidity
// In addSupportedToken, add:
function addSupportedToken(address token, address oracle, address bridge, uint256 _feeBps)
    external onlyRole(TIMELOCK_ROLE)
{
    // ... existing checks ...
    tokenFeeBps[token] = _feeBps;
    // ...
}
```

### Proof of Concept
1. Admin calls `addSupportedToken(wstETH, oracle, bridge)` on `RSETHPool` (Arbitrum). `tokenFeeBps[wstETH]` is `0`.
2. User calls `deposit(wstETH, 10 ether, "ref")`.
3. `viewSwapRsETHAmountAndFee(10 ether, wstETH)` computes `fee = 10 ether * 0 / 10_000 = 0`.
4. `feeEarnedInToken[wstETH] += 0` — no fee is recorded.
5. User receives rsETH equivalent to the full `10 ether` of wstETH at the oracle rate, paying zero protocol fee.
6. Compare: an ETH depositor of the same value pays `feeBps` (e.g., 10 bps = 0.1%) to the protocol. [6](#0-5) [7](#0-6)

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

**File:** contracts/pools/RSETHPool.sol (L311-320)
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
