### Title
`msg.sender` Used as wrsETH Mint Recipient Enables Token Theft When Depositing via Intermediate Contracts - (File: contracts/pools/RSETHPoolV3.sol)

### Summary
All L2 pool `deposit()` functions unconditionally mint `wrsETH` to `msg.sender` with no recipient parameter. When a user deposits ETH or LSTs through any intermediate contract (router, aggregator, multicaller), the intermediate contract becomes `msg.sender` and receives the minted `wrsETH` instead of the actual user, resulting in direct theft of the user's deposited value.

### Finding Description
Every pool variant's `deposit()` function mints `wrsETH` directly to `msg.sender`:

```solidity
// RSETHPoolV3.sol – ETH deposit
wrsETH.mint(msg.sender, rsETHAmount);   // line 262

// RSETHPoolV3.sol – token deposit
wrsETH.mint(msg.sender, rsETHAmount);   // line 290
```

The same pattern is replicated verbatim across `RSETHPoolV3ExternalBridge.sol` (lines 381, 409), `RSETHPoolV3WithNativeChainBridge.sol` (lines 298, 326), `RSETHPoolV2ExternalBridge.sol` (line 298), `RSETHPoolV2.sol` (line 216), and `RSETHPoolV2NBA.sol` (line 115). None of these functions accept a `recipient` parameter.

When a user interacts with the pool through any intermediate contract — a DEX aggregator, a multicall router, a yield optimizer, or a custom wrapper — the call stack is:

```
User EOA → Intermediate Contract → RSETHPoolV3.deposit()
```

Inside `deposit()`, `msg.sender` resolves to the intermediate contract, not the user. The pool mints `wrsETH` to the intermediate contract. The user's ETH (or LST) is consumed by the pool, but the `wrsETH` representing that value lands in the intermediate contract's balance. If the intermediate contract does not explicitly forward the minted tokens to the user (by design or by exploit), the user suffers a total loss of deposited value.

### Impact Explanation
**Critical — Direct theft of user funds.**

The user deposits ETH or an LST and receives zero `wrsETH`. The full deposited value (minus fee) is captured as `wrsETH` by the intermediate contract. `wrsETH` is a yield-bearing liquid restaking token with real ETH backing; its loss is equivalent to losing the deposited ETH principal.

### Likelihood Explanation
**Low.** Requires the user to route their deposit through an intermediate contract rather than calling the pool directly. This is realistic in practice: DEX aggregators (e.g., 1inch, Paraswap), yield optimizers, and multicall batching contracts are commonly used by DeFi users. A malicious intermediate contract could deliberately exploit this, or a benign router that does not account for the mint-to-caller pattern would silently trap the tokens.

### Recommendation
Add an explicit `recipient` parameter to all `deposit()` functions across every pool variant, and mint `wrsETH` to that address instead of `msg.sender`. For backwards compatibility, default the recipient to `msg.sender` when not specified:

```solidity
function deposit(string memory referralId, address recipient) external payable ... {
    ...
    wrsETH.mint(recipient, rsETHAmount);
}
```

Apply the same change to `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV2`, and `RSETHPoolV2NBA`.

### Proof of Concept

1. Attacker deploys `MaliciousRouter`:
   ```solidity
   contract MaliciousRouter {
       function deposit(address pool, string calldata ref) external payable {
           // calls pool with msg.value; wrsETH minted to address(this), not msg.sender
           IRSETHPoolV3(pool).deposit{value: msg.value}(ref);
           // attacker drains wrsETH from this contract
       }
   }
   ```
2. Victim calls `MaliciousRouter.deposit{value: 1 ether}(pool, "ref")`.
3. `RSETHPoolV3.deposit()` executes: `wrsETH.mint(msg.sender, rsETHAmount)` where `msg.sender == address(MaliciousRouter)`.
4. `MaliciousRouter` now holds the minted `wrsETH`; victim receives nothing.
5. Attacker withdraws `wrsETH` from `MaliciousRouter`.

The victim loses 1 ETH worth of `wrsETH`. The same attack applies to token deposits via `deposit(address token, uint256 amount, string referralId)`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

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

**File:** contracts/pools/RSETHPoolV3.sol (L271-293)
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

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L366-412)
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

    /// @dev Swaps supported token for rsETH
    /// @param token The token address
    /// @param amount The amount of token
    /// @param referralId The referral id
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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L282-329)
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

    /// @dev Swaps supported token for rsETH
    /// @param token The token address
    /// @param amount The amount of token
    /// @param referralId The referral id
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

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L289-301)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value) {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L207-219)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value) {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV2NBA.sol (L106-118)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```
