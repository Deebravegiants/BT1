Audit Report

## Title
Cross-Token Withdrawal Enables Theft of Yield Differential Between Allowed Tokens — (`contracts/L2/RsETHTokenWrapper.sol`)

## Summary
`RsETHTokenWrapper` mints wrsETH 1:1 for any allowed token and burns wrsETH 1:1 to release any allowed token the caller specifies, with no binding between the deposited and withdrawn token and no rate check. When `TIMELOCK_ROLE` adds a second allowed token whose market value has diverged from the first (a realistic outcome for yield-bearing bridge tokens), any unprivileged caller can deposit the cheaper token and withdraw the more-valuable token, extracting the yield differential at the expense of other depositors.

## Finding Description
`_deposit` (L134–141) accepts any `allowedTokens[_asset] == true` token, transfers it in, and mints an equal amount of wrsETH:

```solidity
ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);
_mint(_to, _amount);
```

`_withdraw` (L120–128) burns wrsETH and transfers whichever allowed token the caller names:

```solidity
if (!allowedTokens[_asset]) revert TokenNotAllowed();
_burn(msg.sender, _amount);
ERC20Upgradeable(_asset).safeTransfer(_to, _amount);
```

The sole guard is the `allowedTokens` membership check. There is no per-user deposit record, no per-token share accounting, and no exchange-rate oracle. wrsETH is fully fungible across all allowed tokens.

`addAllowedToken` (L174–176) is a normal, intended protocol operation gated only by `TIMELOCK_ROLE`. Once a second token is added and the wrapper holds a balance of it, the cross-token swap is immediately available to any caller.

rsETH is a yield-bearing token whose exchange rate against ETH increases over time. Different L2 bridge implementations (e.g., a static-balance bridge token vs. a rate-accumulating one) will diverge in value as yield accrues. Even a 0.1% divergence is immediately exploitable with zero risk to the attacker.

**Attack path:**
1. `TIMELOCK_ROLE` calls `addAllowedToken(tokenB)` — a legitimate protocol operation.
2. The wrapper accumulates a balance of `tokenB` (e.g., via `depositBridgerAssets` or other depositors).
3. Attacker calls `deposit(tokenA, N)` — mints `N` wrsETH against the cheaper token.
4. Attacker calls `withdraw(tokenB, N)` — burns `N` wrsETH, receives `N` units of the more-valuable token.

Profit = `N × (P_B − P_A)` ETH-equivalent, stolen from depositors of `tokenB`.

## Impact Explanation
**High — Theft of unclaimed yield.** The attacker extracts the yield differential between two allowed tokens. The loss falls directly on depositors of the higher-value token: their collateral is replaced with the cheaper token, leaving their wrsETH under-collateralized. The wrapper's total ETH-value backing decreases permanently for remaining holders. This matches the allowed impact "High. Theft of unclaimed yield."

## Likelihood Explanation
**Medium.** All three preconditions are plausible in normal protocol operation:
- `TIMELOCK_ROLE` adding a second allowed token is an explicitly supported and expected protocol operation (the `addAllowedToken` function exists for this purpose).
- The wrapper accumulating a balance of the higher-value token is routine (via `depositBridgerAssets` or user deposits).
- Value divergence between two bridge representations of a yield-bearing token is realistic and grows over time.

The attack requires no special role, no front-running, no flash loan, and no external protocol compromise — only standard `deposit` + `withdraw` calls.

## Recommendation
1. **Per-token share accounting:** Replace the single wrsETH supply with per-token share tracking. Each deposit of `tokenX` mints shares denominated in `tokenX`, and withdrawals of `tokenX` are bounded by shares minted against `tokenX`.
2. **Enforce a single canonical token:** If all allowed tokens are always intended to be 1:1 equivalent, enforce this with an on-chain rate oracle check in `_withdraw` that reverts if the rate deviates beyond a tight bound (e.g., 0.05%).
3. **Restrict cross-token withdrawals:** Require that `withdraw(asset, amount)` can only be called with the same `asset` that was deposited, tracked per user or per wrsETH mint event.

## Proof of Concept
The submitted Foundry test is complete and reproducible. It deploys two mock ERC20 tokens representing two bridge variants of rsETH, initializes the wrapper with `tokenA`, adds `tokenB` via `addAllowedToken`, has a victim deposit 100 `tokenB`, then has an attacker deposit 100 `tokenA` and withdraw 100 `tokenB`. The final assertions confirm:
- `tokenB.balanceOf(attacker) == 100e18` (attacker received the higher-value token)
- `tokenA.balanceOf(wrapper) == 100e18` (wrapper is left with the cheaper token)
- The victim's wrsETH is now backed only by `tokenA`, not the `tokenB` they deposited

No privileged access is used in the attack steps — only standard public `deposit` and `withdraw` calls on unmodified production code. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

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

**File:** contracts/L2/RsETHTokenWrapper.sol (L174-176)
```text
    function addAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
        _addAllowedToken(_asset);
    }
```
