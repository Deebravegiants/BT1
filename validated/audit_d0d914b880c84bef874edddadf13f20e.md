Audit Report

## Title
Uninitialized `tokenFeeBps` Mapping Causes Zero Protocol Fee on All ERC-20 Token Deposits - (File: contracts/pools/RSETHPool.sol)

## Summary
`RSETHPool.sol` maintains a per-token fee mapping `tokenFeeBps[token]` that is read by the token deposit path but is never initialized when a token is added via `addSupportedToken`. Because Solidity mappings default to zero, every ERC-20 token deposit pays zero protocol fee from the moment the token is added until an admin separately calls `setTokenFeeBps`. ETH depositors pay the configured `feeBps`; token depositors pay nothing, causing permanent loss of fee revenue for the protocol treasury.

## Finding Description

**ETH deposit path** (`viewSwapRsETHAmountAndFee(uint256 amount)`, RSETHPool.sol L311–312):
```solidity
fee = amount * feeBps / 10_000;
```
`feeBps` is set at initialization and is non-zero in production.

**Token deposit path** (`viewSwapRsETHAmountAndFee(uint256 amount, address token)`, RSETHPool.sol L335–336):
```solidity
uint256 feeBpsForToken = tokenFeeBps[token];
fee = amount * feeBpsForToken / 10_000;
```
`tokenFeeBps[token]` is a Solidity mapping declared at L88 that defaults to `0` for every key.

**Root cause — `addSupportedToken` never writes `tokenFeeBps[token]`** (RSETHPool.sol L637–655):
```solidity
function addSupportedToken(address token, address oracle, address bridge) external onlyRole(TIMELOCK_ROLE) {
    ...
    supportedTokenList.push(token);
    supportedTokenOracle[token] = oracle;
    tokenBridge[token] = bridge;
    // tokenFeeBps[token] is never set here
    emit AddSupportedToken(token, oracle, bridge);
}
```

A separate setter `setTokenFeeBps` exists (L583–594) but is not called during token registration and is not enforced or prompted by the contract. The gap between `addSupportedToken` and a subsequent `setTokenFeeBps` call — which may never occur — leaves `tokenFeeBps[token] == 0` indefinitely.

The `deposit(address token, uint256 amount, string referralId)` function at L284–305 calls `viewSwapRsETHAmountAndFee(amount, token)` and accumulates `feeEarnedInToken[token] += fee`, which will always be `+= 0` while the mapping is uninitialized.

**Note on other pool variants:** The claim that `RSETHPoolNoWrapper`, `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolV3WithNativeChainBridge` share the same defect is inaccurate. Those contracts use the global `feeBps` variable (not a per-token mapping) in their token deposit `viewSwapRsETHAmountAndFee(amount, token)` overloads (e.g., RSETHPoolNoWrapper.sol L301, RSETHPoolV3.sol L324), so token depositors in those contracts pay the same global fee as ETH depositors. The vulnerability is confined to `RSETHPool.sol`.

## Impact Explanation

Every ERC-20 token deposit processed through `RSETHPool.sol` while `tokenFeeBps[token] == 0` yields `fee = 0`. The protocol treasury receives zero fee revenue from the token deposit path. This is a concrete, ongoing loss of protocol fee income — yield that the protocol is designed to collect but does not. This matches the allowed impact: **High — Theft of unclaimed yield**.

## Likelihood Explanation

The zero-fee state is the default for every newly added token and requires no attacker action. Any unprivileged user who calls `deposit(token, amount, referralId)` while the default persists pays zero fee. No special privileges, conditions, or victim mistakes are required. The window lasts from token addition until an admin separately calls `setTokenFeeBps`, which is not enforced or prompted by the contract and may never occur. The path is fully reachable by any external depositor.

**Likelihood: High.**

## Recommendation

Add a `_feeBps` parameter to `addSupportedToken` and write it atomically during token registration:

```solidity
function addSupportedToken(
    address token,
    address oracle,
    address bridge,
    uint256 _feeBps
) external onlyRole(TIMELOCK_ROLE) {
    if (_feeBps > 10_000) revert InvalidFeeAmount();
    ...
    supportedTokenList.push(token);
    supportedTokenOracle[token] = oracle;
    tokenBridge[token] = bridge;
    tokenFeeBps[token] = _feeBps;   // initialize atomically
    emit AddSupportedToken(token, oracle, bridge);
}
```

This mirrors how `feeBps` is set for ETH at initialization and eliminates the inconsistency between the two deposit paths.

## Proof of Concept

1. Admin calls `addSupportedToken(wstETH, oracle, bridge)` — `tokenFeeBps[wstETH]` remains `0`.
2. User calls `deposit(wstETH, 10 ether, "ref")` (RSETHPool.sol L284).
3. Internally calls `viewSwapRsETHAmountAndFee(10 ether, wstETH)` (L298).
4. `feeBpsForToken = tokenFeeBps[wstETH] = 0` → `fee = 10 ether * 0 / 10_000 = 0` (L335–336).
5. `feeEarnedInToken[wstETH] += 0` (L300) — protocol collects nothing.
6. The same user depositing `10 ether` of native ETH via `deposit("ref")` would pay `10 ether * feeBps / 10_000` (e.g., 5 bps → 0.005 ETH).
7. The two paths are inconsistent; all token volume is fee-free until an admin intervenes.

**Foundry test plan:**
```solidity
function test_tokenDepositZeroFee() public {
    // Setup: add token with no subsequent setTokenFeeBps call
    vm.prank(timelockAdmin);
    pool.addSupportedToken(address(wstETH), oracle, bridge);

    // Deposit token as unprivileged user
    uint256 amount = 10 ether;
    deal(address(wstETH), user, amount);
    vm.startPrank(user);
    wstETH.approve(address(pool), amount);
    pool.deposit(address(wstETH), amount, "ref");
    vm.stopPrank();

    // Assert zero fee collected
    assertEq(pool.feeEarnedInToken(address(wstETH)), 0);
    // Assert non-zero fee would be collected for ETH
    assertGt(pool.feeBps(), 0);
}
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

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

**File:** contracts/pools/RSETHPool.sol (L311-312)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
```

**File:** contracts/pools/RSETHPool.sol (L335-336)
```text
        uint256 feeBpsForToken = tokenFeeBps[token];
        fee = amount * feeBpsForToken / 10_000;
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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L300-302)
```text
    {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```

**File:** contracts/pools/RSETHPoolV3.sol (L323-325)
```text
    {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;
```
