The vulnerability is real and concrete. Let me trace through the exact code path.

### Title
Cross-Token Arbitrage Drains Higher-Value Reserves in `RsETHTokenWrapper` — (`contracts/L2/RsETHTokenWrapper.sol`)

---

### Summary

`RsETHTokenWrapper` supports multiple allowed tokens via a `mapping(address => bool) allowedTokens` and mints/burns wrsETH at a strict 1:1 ratio for any allowed token. Because `_deposit` and `_withdraw` perform no cross-token accounting and no price check, any unprivileged user can deposit the cheaper allowed token to receive wrsETH and immediately withdraw the more expensive allowed token at the same nominal amount, extracting value from the wrapper and leaving it undercollateralized.

---

### Finding Description

The contract is explicitly designed to hold multiple alternative rsETH tokens:

- `initialize` adds the first token. [1](#0-0) 
- `reinitialize` adds a second token via an intended admin upgrade. [2](#0-1) 
- `addAllowedToken` (gated by `TIMELOCK_ROLE`) can add further tokens at any time. [3](#0-2) 

`_deposit` only checks `allowedTokens[_asset]`, then mints `_amount` wrsETH regardless of which token is deposited: [4](#0-3) 

`_withdraw` only checks `allowedTokens[_asset]`, then burns `_amount` wrsETH and transfers `_amount` of the *requested* token — with no constraint that it must be the same token that was deposited: [5](#0-4) 

There is no per-token reserve accounting, no price oracle, and no restriction preventing a caller from depositing token-A and withdrawing token-B. The entire multi-token pool is treated as a single fungible bucket at 1:1 with wrsETH.

---

### Impact Explanation

**Critical — Protocol insolvency / direct theft of funds.**

When two allowed tokens trade at different market prices (e.g., altRsETH-A at 0.98 ETH and altRsETH-B at 1.00 ETH), an attacker can:

1. Deposit N units of token-A (cheap) → receive N wrsETH.
2. Withdraw N units of token-B (expensive) → burn N wrsETH, receive N token-B.

Net gain per iteration: `N × (price_B − price_A)`. The wrapper's token-B reserves are drained while token-A accumulates. Remaining wrsETH holders who try to withdraw token-B will find insufficient balance; the wrapper is insolvent with respect to the higher-value asset.

---

### Likelihood Explanation

**High.** The multi-token design is intentional — `reinitialize` was added specifically to introduce a second token. L2 deployments routinely have multiple bridge-issued versions of the same L1 token (native bridge vs. third-party bridge), and these routinely trade at a spread due to differing bridge risk and liquidity. No special privilege is required to execute the exploit once two tokens are registered; `deposit` and `withdraw` are fully public. [6](#0-5) [7](#0-6) 

---

### Recommendation

1. **Per-token reserve accounting**: Track how much of each allowed token backs the outstanding wrsETH supply. On `_withdraw`, only allow redemption of the token that was originally deposited (i.e., record a per-user or per-token liability), or enforce that the total wrsETH redeemable against token-X cannot exceed the wrapper's balance of token-X.

2. **Alternatively, enforce single-token redemption**: Require that `withdraw(asset, amount)` can only succeed if `balanceOf(asset, wrapper) >= amount` *and* the caller's wrsETH was minted against that specific asset (requires deposit receipts or per-token sub-accounting).

3. **Price-parity guard**: If multi-token fungibility is intentional, integrate an oracle and reject deposits/withdrawals when the price spread between any two allowed tokens exceeds a configured threshold.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.27;

// Assume:
//   tokenA.price = 0.98 ETH  (cheaper, e.g. third-party bridge version)
//   tokenB.price = 1.00 ETH  (more expensive, e.g. native bridge version)
//   Both are in allowedTokens.
//   Wrapper holds 1000 tokenB (deposited by legitimate users).

function testCrossTokenArbitrage() public {
    uint256 amount = 1000e18;

    // Attacker acquires 1000 tokenA at market price (costs ~980 ETH equivalent)
    tokenA.mint(attacker, amount);

    vm.startPrank(attacker);

    // Step 1: deposit cheap tokenA → mint 1000 wrsETH at 1:1
    tokenA.approve(address(wrapper), amount);
    wrapper.deposit(address(tokenA), amount);
    // wrapper now holds: 1000 tokenA + 1000 tokenB, supply = 2000 wrsETH

    // Step 2: withdraw expensive tokenB → burn 1000 wrsETH, receive 1000 tokenB
    wrapper.withdraw(address(tokenB), amount);
    // wrapper now holds: 1000 tokenA + 0 tokenB, supply = 1000 wrsETH
    // All remaining wrsETH is backed only by tokenA (worth ~980 ETH)
    // wrsETH is now undercollateralized; original tokenB depositors cannot redeem

    vm.stopPrank();

    // Assert: wrapper tokenB balance is zero
    assertEq(tokenB.balanceOf(address(wrapper)), 0);
    // Assert: wrsETH supply (1000) > tokenB balance (0) → insolvency
    assertGt(wrapper.totalSupply(), tokenB.balanceOf(address(wrapper)));
}
```

The root cause is at lines 120–128 and 134–141 of `contracts/L2/RsETHTokenWrapper.sol`: `_withdraw` has no guard preventing redemption of a different token than was deposited, and `_deposit` performs no per-token reserve tracking. [8](#0-7)

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L47-49)
```text
    function reinitialize(address _altRsETH) external reinitializer(2) onlyRole(DEFAULT_ADMIN_ROLE) {
        _addAllowedToken(_altRsETH);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L55-64)
```text
    function initialize(address admin, address bridger, address _altRsETH) external initializer {
        __ERC20_init("rsETHWrapper", "wrsETH");
        __ERC20Permit_init("rsETHWrapper");
        __AccessControl_init();

        _setupRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(BRIDGER_ROLE, bridger);

        _addAllowedToken(_altRsETH);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L69-71)
```text
    function deposit(address asset, uint256 _amount) external {
        _deposit(asset, msg.sender, _amount);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L84-86)
```text
    function withdraw(address asset, uint256 _amount) external {
        _withdraw(asset, msg.sender, _amount);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L120-141)
```text
    function _withdraw(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        _burn(msg.sender, _amount);

        ERC20Upgradeable(_asset).safeTransfer(_to, _amount);

        emit Withdraw(_asset, msg.sender, _to, _amount);
    }

    /// @notice Deposit tokens into the lockbox
    /// @param _asset The address of the token to deposit
    /// @param _to The address to send the XERC20 to
    /// @param _amount The amount of tokens to deposit
    function _deposit(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        _mint(_to, _amount);
        emit Deposit(_asset, msg.sender, _to, _amount);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L174-176)
```text
    function addAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
        _addAllowedToken(_asset);
    }
```
