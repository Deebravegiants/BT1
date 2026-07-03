### Title
Cross-Token Withdrawal Allows wrsETH Holders to Drain Any Allowed Token Reserve - (File: contracts/L2/RsETHTokenWrapper.sol)

---

### Summary

`RsETHTokenWrapper` supports multiple allowed tokens but issues a single fungible `wrsETH` token with no per-token accounting. Any `wrsETH` holder can call `withdraw(tokenB, amount)` regardless of which token they originally deposited, draining another token's reserves and leaving depositors of that token unable to redeem.

---

### Finding Description

The `_withdraw` function performs only two checks before transferring tokens out:

1. The requested `_asset` is in `allowedTokens`
2. The caller holds sufficient `wrsETH` to burn [1](#0-0) 

There is no record of which token a depositor originally contributed. The `_deposit` function mints generic `wrsETH` against any allowed token: [2](#0-1) 

Because `wrsETH` is fully fungible across all allowed token types, a holder who deposited `tokenA` can freely call `withdraw(tokenB, amount)` and receive `tokenB`, consuming reserves that belong to `tokenB` depositors.

---

### Impact Explanation

- No funds leave the system in aggregate (total token value in the contract equals total `wrsETH` supply, assuming 1:1 peg between all allowed tokens).
- However, the contract fails to deliver the specific token a depositor expects to redeem. A user who deposited `tokenB` may find the contract holds zero `tokenB` and cannot redeem their `wrsETH` for `tokenB` at all — they are forced to accept `tokenA` instead, or wait.
- This matches **Low — Contract fails to deliver promised returns, but doesn't lose value**.

---

### Likelihood Explanation

- Requires only that two or more tokens are simultaneously in `allowedTokens`, which is the intended multi-token design (`reinitialize` adds a second token; `addAllowedToken` can add more).
- Any ordinary user can trigger this with a single public call — no role, no front-running, no oracle dependency.
- Likelihood is **High** once a second allowed token exists. [3](#0-2) [4](#0-3) 

---

### Recommendation

Track per-token balances owed to depositors, or restrict each `wrsETH` mint/burn to a single canonical token (i.e., enforce that `withdraw` can only redeem the same token type that was deposited, using a per-user or per-token accounting mapping). Alternatively, if all allowed tokens are truly interchangeable at 1:1, document this explicitly and ensure the UI/UX communicates that users may receive a different allowed token on withdrawal.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.27;

// Assume tokenA and tokenB are both added to allowedTokens.
// Both are 1:1 alt-rsETH tokens.

// Step 1: userA deposits 100e18 tokenA
wrapper.deposit(tokenA, 100e18);
// wrapper holds: 100e18 tokenA, 0 tokenB
// wrsETH supply: 100e18 (userA holds all)

// Step 2: userB deposits 100e18 tokenB
wrapper.deposit(tokenB, 100e18);  // called by userB
// wrapper holds: 100e18 tokenA, 100e18 tokenB
// wrsETH supply: 200e18

// Step 3: userA withdraws tokenB (not what they deposited)
wrapper.withdraw(tokenB, 100e18);
// _withdraw: allowedTokens[tokenB] == true ✓
// burns 100e18 wrsETH from userA ✓
// transfers 100e18 tokenB to userA ✓  ← drains tokenB reserve
// wrapper holds: 100e18 tokenA, 0 tokenB
// wrsETH supply: 100e18 (userB holds all)

// Step 4: userB tries to redeem their wrsETH for tokenB
wrapper.withdraw(tokenB, 100e18);  // called by userB
// ERC20: transfer amount exceeds balance → REVERTS
// userB cannot get tokenB back; must accept tokenA instead
```

The root cause is that `_withdraw` at line 121 only validates `allowedTokens[_asset]` and then unconditionally transfers `_asset` — there is no linkage between the token deposited and the token redeemable. [1](#0-0)

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L24-24)
```text
    mapping(address allowedToken => bool isAllowed) public allowedTokens;
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L47-49)
```text
    function reinitialize(address _altRsETH) external reinitializer(2) onlyRole(DEFAULT_ADMIN_ROLE) {
        _addAllowedToken(_altRsETH);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L120-128)
```text
    function _withdraw(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        _burn(msg.sender, _amount);

        ERC20Upgradeable(_asset).safeTransfer(_to, _amount);

        emit Withdraw(_asset, msg.sender, _to, _amount);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L134-141)
```text
    function _deposit(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        _mint(_to, _amount);
        emit Deposit(_asset, msg.sender, _to, _amount);
    }
```
