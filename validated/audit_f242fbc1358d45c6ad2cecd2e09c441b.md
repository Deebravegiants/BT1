Looking at the contract carefully, I need to trace the exact math of the cap formula across multiple allowed tokens.

### Title
Per-Asset Cap Formula Allows Aggregate Collateral to Exceed `totalSupply`, Stranding Excess Tokens — (`contracts/L2/RsETHTokenWrapper.sol`)

---

### Summary

`maxAmountToDepositBridgerAsset` computes each allowed token's deposit cap independently as `totalSupply - balance[_asset]`. When two or more tokens are allowed, the BRIDGER_ROLE can fill each token's cap in sequence, depositing a combined collateral that is a multiple of `totalSupply`. The surplus collateral can never be redeemed because the total wrsETH supply bounds all withdrawals, leaving the excess permanently stranded.

---

### Finding Description

`maxAmountToDepositBridgerAsset` is defined as:

```solidity
return wrsETHSupply - balanceOfAssetInWrapper;   // line 109
``` [1](#0-0) 

The formula is **per-asset**: it subtracts only the balance of the queried token from `totalSupply`. It does not subtract the balances of any other allowed tokens. When a second allowed token exists, its balance is zero, so its cap equals the full `totalSupply` regardless of how much of the first token has already been deposited.

`depositBridgerAssets` enforces only this per-asset cap:

```solidity
if (maxAmountToDepositBridgerAsset(_asset) < _amount) revert CannotDeposit();
``` [2](#0-1) 

No mint occurs in `depositBridgerAssets`; it only transfers tokens in to back already-minted wrsETH. [3](#0-2) 

**Concrete execution path:**

| Step | Action | `balance[A]` | `balance[B]` | `totalSupply` |
|------|--------|-------------|-------------|--------------|
| 0 | MINTER_ROLE mints 100 wrsETH | 0 | 0 | 100 |
| 1 | `depositBridgerAssets(tokenA, 100)` — cap = 100−0 = 100 ✓ | 100 | 0 | 100 |
| 2 | `depositBridgerAssets(tokenB, 100)` — cap = 100−0 = 100 ✓ | 100 | 100 | 100 |

After step 2: total collateral = 200, wrsETH supply = 100. Only 100 units of collateral can ever be redeemed. The remaining 100 units (whichever token users do not choose to withdraw) are permanently stranded.

`_withdraw` burns wrsETH 1-for-1 against a single chosen asset:

```solidity
_burn(msg.sender, _amount);
ERC20Upgradeable(_asset).safeTransfer(_to, _amount);
``` [4](#0-3) 

Once all 100 wrsETH are burned to redeem tokenA, no wrsETH remains to redeem tokenB. If `removeAllowedToken(tokenB)` is subsequently called, `_withdraw` reverts at the `TokenNotAllowed` guard:

```solidity
if (!allowedTokens[_asset]) revert TokenNotAllowed();
``` [5](#0-4) 

making the stranded tokenB permanently irrecoverable with no rescue path in the contract.

---

### Impact Explanation

The contract promises that deposited collateral backs outstanding wrsETH 1-for-1. The broken aggregate cap allows the BRIDGER_ROLE — acting entirely within its granted permissions — to deposit collateral whose total value exceeds `totalSupply`. The surplus is permanently locked: there is no admin sweep, no rescue function, and no way to mint additional wrsETH to redeem it. This matches **Low — contract fails to deliver promised returns, but doesn't lose value** (the stranded tokens remain in the contract but are unreachable).

---

### Likelihood Explanation

Likelihood is low. It requires:
1. Two or more tokens simultaneously in `allowedTokens` (supported by `addAllowedToken`/`reinitialize`).
2. The BRIDGER_ROLE depositing both tokens up to their individual caps.

The BRIDGER_ROLE is trusted and the scenario requires no compromise — only the BRIDGER_ROLE acting within its intended permissions against a flawed formula.

---

### Recommendation

Replace the per-asset cap with an aggregate cap that accounts for all collateral already held:

```solidity
function maxAmountToDepositBridgerAsset(address _asset) public view returns (uint256) {
    if (!allowedTokens[_asset]) return 0;
    uint256 wrsETHSupply = totalSupply();
    uint256 totalCollateral = _totalCollateral(); // sum of balances for all allowed tokens
    if (totalCollateral >= wrsETHSupply) return 0;
    return wrsETHSupply - totalCollateral;
}
```

This requires tracking allowed token addresses in an enumerable structure (e.g., `EnumerableSet`) so `_totalCollateral()` can iterate over them.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.27;

// Pseudocode — run on a local fork or Foundry test
function testAggregateCapExceeded() public {
    // Setup: admin grants roles, two mock altRsETH tokens (tokenA, tokenB) added
    wrapper.addAllowedToken(address(tokenA));   // via TIMELOCK_ROLE
    wrapper.addAllowedToken(address(tokenB));   // via TIMELOCK_ROLE

    // MINTER_ROLE mints 100 wrsETH (simulating L2 bridge mint)
    wrapper.mint(user, 100e18);
    assertEq(wrapper.totalSupply(), 100e18);

    // BRIDGER_ROLE deposits tokenA up to its cap
    uint256 capA = wrapper.maxAmountToDepositBridgerAsset(address(tokenA));
    assertEq(capA, 100e18);  // cap = totalSupply - balance[A] = 100 - 0
    tokenA.approve(address(wrapper), capA);
    wrapper.depositBridgerAssets(address(tokenA), capA);  // succeeds

    // BRIDGER_ROLE deposits tokenB up to its cap — should fail but doesn't
    uint256 capB = wrapper.maxAmountToDepositBridgerAsset(address(tokenB));
    assertEq(capB, 100e18);  // cap = totalSupply - balance[B] = 100 - 0 (BUG)
    tokenB.approve(address(wrapper), capB);
    wrapper.depositBridgerAssets(address(tokenB), capB);  // succeeds — BUG

    // Total collateral = 200e18 > totalSupply = 100e18
    assertGt(
        tokenA.balanceOf(address(wrapper)) + tokenB.balanceOf(address(wrapper)),
        wrapper.totalSupply()
    );

    // User redeems all wrsETH for tokenA — tokenB is now stranded
    vm.prank(user);
    wrapper.withdraw(address(tokenA), 100e18);
    assertEq(wrapper.totalSupply(), 0);
    assertEq(tokenB.balanceOf(address(wrapper)), 100e18);  // permanently stranded
}
```

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L99-110)
```text
    function maxAmountToDepositBridgerAsset(address _asset) public view returns (uint256) {
        if (!allowedTokens[_asset]) return 0;

        // get totalSupply of wrsETH minted
        uint256 wrsETHSupply = totalSupply();
        // balance of _asset with the contract
        uint256 balanceOfAssetInWrapper = ERC20Upgradeable(_asset).balanceOf(address(this));

        if (balanceOfAssetInWrapper > wrsETHSupply) return 0;

        return wrsETHSupply - balanceOfAssetInWrapper;
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L121-121)
```text
        if (!allowedTokens[_asset]) revert TokenNotAllowed();
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L123-125)
```text
        _burn(msg.sender, _amount);

        ERC20Upgradeable(_asset).safeTransfer(_to, _amount);
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L162-170)
```text
    function depositBridgerAssets(address _asset, uint256 _amount) external onlyRole(BRIDGER_ROLE) {
        if (maxAmountToDepositBridgerAsset(_asset) < _amount) {
            revert CannotDeposit();
        }

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        emit BridgerDeposited(_asset, msg.sender, _amount);
    }
```
