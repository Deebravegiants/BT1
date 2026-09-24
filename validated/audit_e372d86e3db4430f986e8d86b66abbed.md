### Title
Permit signature does not bind the downstream trade parameters, letting an attacker replay a captured signature to redirect a victim's USDC into an arbitrary token/referrer - ([File: packages/contracts/src/Zap.sol])

### Summary
`Zap.buyWithPermit`, `Zap.sellWithPermit`, and `Zap.createTokenWithPermit` accept a `PermitData` struct that is EIP-2612 signed over only `(owner, spender, value, nonce, deadline)`, while the actual trade parameters — `tokenAddress`, `usdcAmount`/`tokenAmount`, `minTokensOut`/`minUsdcOut`, and `referrer` — are separate, unauthenticated call arguments that are never bound to the signature. This is the same bug class as the reported oracle report: a value that determines the semantic meaning/effect of a signed action (there: `offset`; here: which token is traded, at what size, and who gets referral credit) is left out of what the signature actually authenticates.

### Finding Description
`_tryPermit` only verifies the ERC-2612 `permit()` signature to grant `Zap` an allowance for `p.value` USDC (or Token, for sells): [1](#0-0) 

The wrapper functions then call `_buyInternal`/`_sellInternal` using entirely separate, caller-supplied parameters (`tokenAddress`, `usdcAmount`, `minTokensOut`, `referrer`) that are not part of the signed message at all: [2](#0-1) [3](#0-2) 

Because these functions are `external` and permissionless, anyone who obtains a valid `(v, r, s)` for a given `owner`/`value`/`deadline` (which is necessarily visible in the mempool the moment the legitimate user submits their `buyWithPermit`/`sellWithPermit` transaction — the code's own comments acknowledge permits are frontrunnable) can submit their own transaction reusing that exact signature but substituting any `tokenAddress`, `referrer`, and `usdcAmount ≤ p.value`/`minTokensOut = 0` they like. The permit's `spender` is fixed to `Zap` itself, so it authorizes `Zap` to pull funds generically — it says nothing about which of `Zap`'s many trade paths that allowance is used for.

The contract's own documentation already concedes signatures are observable pre-confirmation and designs around it for the narrow nonce-consumption DoS case: [4](#0-3) 

but that defense only protects the allowance-setting step; it does nothing to bind the downstream trade's `tokenAddress`/`referrer`/amounts to the signer's intent.

### Impact Explanation
An attacker who front-runs a pending `buyWithPermit` call can:
- Redirect the victim's signed USDC allowance into a token of the attacker's own choosing (e.g. a token the attacker just launched via `Zap.createToken`), forcing the victim to buy into an attacker-controlled/worthless token instead of the one they intended, with `minTokensOut = 0` set by the attacker to guarantee the call doesn't revert on bad pricing.
- Set `referrer` to their own address, stealing referral attribution/fees that should have gone to the victim's intended referrer.
- Choose `usdcAmount` up to `p.value`, controlling exactly how much of the signed allowance is consumed and on which trade.

This is concrete, unauthorized redirection of a trader's funds into a trade the trader never signed for — a direct funds-safety violation reachable by any unprivileged address, matching the report's underlying root cause (a value governing the meaning of a signed action is excluded from what is actually verified).

### Likelihood Explanation
High reachability: `buyWithPermit`/`sellWithPermit`/`createTokenWithPermit` are all `external` and require no special privilege. The only precondition is observing a pending permit-based transaction in the mempool, which is the normal, expected way these functions are used (a signed off-chain permit submitted on-chain), and which the contract's own docs already treat as an accepted frontrunning surface.

### Recommendation
Bind the downstream trade intent into the same signed message the user produces, e.g. by hashing `tokenAddress`, `usdcAmount`/`tokenAmount`, `minTokensOut`/`minUsdcOut`, and `referrer` into an EIP-712 struct that `Zap` verifies itself (rather than relying solely on the token's generic ERC-2612 `permit`), or at minimum require `usdcAmount == p.value` / `tokenAmount == p.value` and disallow a `referrer` unless it is likewise signed, so a captured signature cannot be replayed against different trade parameters than the ones the signer approved.

### Proof of Concept
1. Victim signs an ERC-2612 permit for `usdc.permit(victim, Zap, 100e6, deadline, v, r, s)` and broadcasts `zap.buyWithPermit(TOKEN_X, 100e6, minOut, referrerA, p)`.
2. Attacker observes the pending tx in the mempool, extracts `p = (100e6, deadline, v, r, s)`.
3. Attacker submits `zap.buyWithPermit(TOKEN_ATTACKER, 100e6, 0, attackerAddr, p)` with higher gas, landing first.
4. `_tryPermit` succeeds (signature only checks `owner`, `spender=Zap`, `value`, `nonce`, `deadline` — all satisfied), granting `Zap` a 100e6 USDC allowance from the victim.
5. `_buyInternal` pulls 100e6 USDC from the victim and buys `TOKEN_ATTACKER` (attacker's chosen token) with `minTokensOut = 0`, crediting `attackerAddr` as referrer.
6. Victim's original transaction now reverts (nonce/allowance consumed), but the victim has already had 100e6 USDC spent on a token they never chose, and the attacker collected referral credit.

### Citations

**File:** packages/contracts/src/Zap.sol (L187-196)
```text
    function buyWithPermit(
        address tokenAddress,
        uint256 usdcAmount,
        uint256 minTokensOut,
        address referrer,
        PermitData calldata p
    ) external nonReentrant returns (uint256 tokensOut) {
        _tryPermit(address(_s().usdc), msg.sender, p);
        return _buyInternal(tokenAddress, usdcAmount, minTokensOut, referrer);
    }
```

**File:** packages/contracts/src/Zap.sol (L206-214)
```text
    function sellWithPermit(
        address tokenAddress,
        uint256 tokenAmount,
        uint256 minUsdcOut,
        PermitData calldata p
    ) external nonReentrant returns (uint256 usdcOut) {
        _tryPermit(tokenAddress, msg.sender, p);
        return _sellInternal(tokenAddress, tokenAmount, minUsdcOut);
    }
```

**File:** packages/contracts/src/Zap.sol (L491-496)
```text
    /// @dev Catch swallows reverts to defuse permit-front-run DoS: if an
    ///      attacker submits the same sig first the nonce is consumed but the
    ///      allowance is already set, so the follow-on `transferFrom`
    ///      succeeds. A genuinely bad permit is caught downstream by the
    ///      transfer reverting on insufficient allowance — frontends should
    ///      simulate to surface a permit-specific error pre-flight.
```

**File:** packages/contracts/src/Zap.sol (L497-503)
```text
    function _tryPermit(
        address token,
        address owner_,
        PermitData calldata p
    ) internal {
        try IERC20Permit(token).permit(owner_, address(this), p.value, p.deadline, p.v, p.r, p.s) {} catch {}
    }
```
