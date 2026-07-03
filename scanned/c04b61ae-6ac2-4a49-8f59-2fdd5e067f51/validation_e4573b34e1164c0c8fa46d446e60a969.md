### Title
Token Deposits in RSETHPool Default to Zero Fees, Allowing Users to Bypass ETH Deposit Fees - (File: contracts/pools/RSETHPool.sol)

### Summary

`RSETHPool.sol` (the Arbitrum pool) maintains two separate fee mechanisms: a global `feeBps` for ETH deposits and a per-token `tokenFeeBps[token]` mapping for ERC20 token deposits. When a new token is added via `addSupportedToken()`, `tokenFeeBps[token]` is never initialized and defaults to `0`. Any user can deposit a supported token (e.g., wstETH) instead of ETH to receive the same `wrsETH` output while paying zero protocol fees, permanently bypassing the ETH deposit fee.

### Finding Description

`RSETHPool.sol` declares two distinct fee storage variables:

- `feeBps` — applied to native ETH deposits
- `tokenFeeBps` — a per-token mapping applied to ERC20 token deposits [1](#0-0) [2](#0-1) 

When computing the fee for a token deposit, the contract reads `tokenFeeBps[token]` directly: [3](#0-2) 

However, `addSupportedToken()` only sets `supportedTokenOracle[token]` and `tokenBridge[token]`; it never initializes `tokenFeeBps[token]`: [4](#0-3) 

Because Solidity mappings default to `0`, every newly added token has `tokenFeeBps[token] == 0`, making `fee = amount * 0 / 10_000 = 0`. The only way to set a non-zero token fee is through a separate admin call to `setTokenFeeBps()`: [5](#0-4) 

By contrast, ETH deposits always apply the global `feeBps`: [6](#0-5) 

This inconsistency is structurally identical to the Footium analog: one deposit path (ETH) has fees enforced; the other (ERC20 tokens) silently has zero fees by default.

Note that the other pool contracts (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPoolNoWrapper`) all use a single shared `feeBps` for both ETH and token deposits, so this issue is unique to `RSETHPool.sol`. [7](#0-6) 

### Impact Explanation

A depositor who would normally pay a fee on ETH deposits can instead deposit an equivalent value of wstETH (or any other supported token) and receive the same `wrsETH` output with zero protocol fee deducted. The protocol permanently loses the fee revenue it intended to collect on that economic value. This constitutes **theft of unclaimed yield** from the protocol.

### Likelihood Explanation

The condition is always present: any supported token added without a subsequent `setTokenFeeBps()` call has a zero fee. A depositor only needs to hold a supported token (e.g., wstETH, which is already integrated) and call `deposit(token, amount, referralId)` instead of the ETH `deposit(referralId)` overload. No special privileges, flash loans, or timing are required.

### Recommendation

Initialize `tokenFeeBps[token]` inside `addSupportedToken()` to the current global `feeBps` (or require an explicit fee parameter), so that newly added tokens are never silently fee-free:

```solidity
function addSupportedToken(address token, address oracle, address bridge, uint256 _feeBps)
    external onlyRole(TIMELOCK_ROLE)
{
    // ... existing checks ...
    tokenFeeBps[token] = _feeBps;
    // ...
}
```

Alternatively, audit all currently supported tokens and call `setTokenFeeBps()` for any that have not yet had their fee set.

### Proof of Concept

1. Protocol sets `feeBps = 30` (0.30% ETH deposit fee).
2. Admin calls `addSupportedToken(wstETH, oracle, bridge)` — `tokenFeeBps[wstETH]` remains `0`.
3. Alice wants to acquire `wrsETH` equivalent to 10 ETH of value.
   - **ETH path**: `deposit{value: 10 ETH}("")` → fee = `10e18 * 30 / 10000 = 0.03 ETH` deducted; Alice receives `rsETHAmount` based on `9.97 ETH`.
   - **Token path**: `deposit(wstETH, wstETHAmount, "")` → `feeBpsForToken = tokenFeeBps[wstETH] = 0`; fee = `0`; Alice receives `rsETHAmount` based on the full `10 ETH` equivalent.
4. Alice uses the token path, receiving more `wrsETH` and paying zero protocol fee, permanently depriving the protocol of the 0.03 ETH fee. [8](#0-7) [9](#0-8)

### Citations

**File:** contracts/pools/RSETHPool.sol (L43-44)
```text
    uint256 public feeBps; // Basis points for fees for ETH deposits
    uint256 public feeEarnedInETH;
```

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

**File:** contracts/pools/RSETHPool.sol (L311-313)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
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

**File:** contracts/pools/RSETHPoolV3.sol (L323-325)
```text
    {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```
