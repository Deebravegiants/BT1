### Title
Tokens, LT, and USDC sent directly to Zap are permanently unrecoverable - no analog to `sweepDonations`/`_sweepLTToOwner` exists on the router-facing entry point ([File: packages/contracts/src/Zap.sol])

### Summary
`Zap` is the sole trader-facing entry point for buys/sells, moving USDC, LT, and Token balances through itself on every call via `transferFrom`/`transfer` (see the buy/sell flow documented in `docs/contracts-scope.md:44-63`) [1](#0-0)  and `Zap.sol`'s stated design (`Buy path: USDC → LT mint → curve buy ... Sell path: token → curve sell ... → LT redeem → USDC`) [2](#0-1) . Unlike `Bonding` and `FeeVault`, which both have explicit, permissionless recovery mechanisms for assets that land in them outside the intended flow — `Bonding._sweepLTToOwner` (emitting `LTRescued`) [3](#0-2)  and `FeeVault.sweepDonations` (emitting `DonationsSwept`) [4](#0-3)  — `Zap.sol` has no equivalent rescue/skim/withdraw function anywhere in its public/external surface (confirmed by grepping for `rescue|Rescued|recoverToken|withdraw|skim` across the file, which only matched an unrelated natspec comment, not an implementation) [5](#0-4) .

### Finding Description
Any unrelated wallet can `IERC20(usdc).transfer(zapAddress, X)`, `IERC20(token).transfer(zapAddress, X)`, or `IERC20(lt).transfer(zapAddress, X)` directly to the `Zap` contract's address instead of going through `buy`/`sell`. Because `Zap`'s buy/sell logic only ever pulls funds it explicitly needs via `transferFrom`/`safeTransferFrom` from `msg.sender` and never sweeps its own idle balance, any asset landed on `Zap` by a bare `transfer` has no code path back out. This is the same root-cause pattern as the reported Diamond issue: an entry point that legitimately receives value in the course of normal operation, but provides no mechanism to reclaim value that arrives outside that normal call flow.

This differs from the protocol's LT/Token donation handling elsewhere, which was explicitly hardened against exactly this class of bug:
- `Bonding` snapshots `protectedLT` and sweeps any residual/stray LT balance to the owner at the end of every `finalizeGraduation` [6](#0-5) .
- `FeeVault.sweepDonations` explicitly exists "because direct USDC transfers would otherwise inflate `balanceOf`... and silently mask the `accrue` underfund check," and is permissionless [4](#0-3) .

`Zap` was not given the same treatment, so it is the one primary trader-facing contract in scope where accidental or intentional direct transfers are unrecoverable.

### Impact Explanation
Any USDC, launched Token, or LT sent directly to `Zap` (e.g. by a user error, a wallet mis-click, or an integrator bug in a frontend/aggregator that resolves the wrong recipient) is permanently locked — there is no owner-only or permissionless recovery path, unlike the equivalent situation in `Bonding` and `FeeVault`. This is a permanent freezing-of-funds bug matching the "Medium" severity class of the reported analog (locked, unrecoverable value sent to a core contract with no withdrawal mechanism).

### Likelihood Explanation
`Zap` is the advertised, documented, user-facing address for every buy/sell interaction (`docs/contracts-scope.md`), so it is a natural target for a stray/mistaken direct transfer by traders, and is also the parking spot that a well-meaning "donation" or a buggy off-chain integration would pick, mirroring how `FeeVault.sweepDonations` anticipates exactly this behavior for USDC. Given `Zap`'s constant interaction with these three asset types, this is a realistically reachable, no-privilege-required scenario.

### Recommendation
Add an owner-restricted (or, for parity with `FeeVault.sweepDonations`/`Bonding`'s auto-sweep, permissionless-but-fixed-recipient) rescue function on `Zap` that sweeps any USDC/Token/LT balance idle in the contract beyond what is required mid-transaction, analogous to `FeeVault.sweepDonations` and `Bonding._sweepLTToOwner`. Ensure it cannot be invoked to drain funds mid-flight during a buy/sell (e.g. gate via `nonReentrant`/balance snapshotting consistent with the rest of the codebase's patterns).

### Proof of Concept
1. A trader or a stray integrator calls `IERC20(usdc).transfer(address(zap), 100e6)` directly (not via `Zap.buy`).
2. `Zap.buy`/`Zap.sell` never read or use `Zap`'s own idle balance beyond what each call pulls via `transferFrom`, so the 100 USDC now sits in `Zap`'s balance with no code path to move it out.
3. Repeat the grep across `packages/contracts/src/Zap.sol` for any `rescue`/`sweep`/`withdraw`/`skim` function — none exists, confirming there is no way for the owner or the depositor to reclaim it, unlike `FeeVault.sweepDonations()` [7](#0-6)  or `Bonding._sweepLTToOwner` [8](#0-7) .

### Citations

**File:** docs/contracts-scope.md (L44-63)
```markdown
## Buy Flow

1. `Zap.buy(tokenAddress, usdcAmount, minTokensOut, referrer)`
2. `Zap` pulls `usdcAmount` USDC and deducts the 0.75% Alt Fun fee up-front (forwarded to `FeeVault`, split 0.5% protocol / 0.25% creator). The fee is charged on every buy — curve **and** post-graduation — not just curve trades.
3. Net USDC is minted to LT
4. If on curve: routes through `Bonding.buy()` (the internal AMM `Router.sol`). If graduated: swaps on HyperSwap V2 (TOKEN/LT pool). The 0.75% Alt Fun fee is identical on both paths; post-grad, HyperSwap also charges its own 0.3% LP fee on the swap leg, on top of the Alt Fun fee.
5. Tokens sent to user; on a capped buy, any LT minted but not consumed by the curve is returned directly as LT, while unconverted USDC and the pro-rata fee over-charge are refunded in USDC

**Overflow buy protection.** On the final buy that would empty the curve, `Router.buy` caps `tokensOut` at the pair's real token balance and back-calculates the LT actually required (`amountInUsed`). `Bonding.buy` returns both `tokensOut` and `amountInUsed`. `Zap.buy` transfers the LT it minted but the curve didn't consume (`ltMinted - amountInUsed`) straight back to the buyer as LT — it is **not** redeemed, since round-tripping the dust overshoot through `redeem()` would re-incur the LT's redemption fee. Net USDC that was never minted into LT, plus the pro-rata fee over-charge, is refunded separately in USDC.

## Sell Flow

1. `Zap.sell(tokenAddress, tokenAmount, minUsdcOut)`
2. If the curve token is already graduatable (LT appreciation pushed it past the threshold), the sell triggers graduation instead of executing — called with `minUsdcOut == 0`, `Zap.sell` calls `Bonding.triggerGraduation` and returns `0`, leaving the seller's tokens untouched so they can exit on the graduated pool. This path emits **no `Sell` event** (nothing is sold); off-chain consumers detect it via `TokenGraduating`/`TokenGraduated`. A positive `minUsdcOut` reverts, since the graduation fills nothing and the `usdcOut >= minUsdcOut` guarantee can't be met. Otherwise, if on curve: routes through `Bonding.sell()` (the internal AMM `Router.sol`). If graduated: swaps on HyperSwap V2 (which charges a 0.3% LP fee on the swap leg, on top of the Alt Fun fee deducted below).
3. LT redeemed atomically via `redeem()` → gross USDC into `Zap`
4. `Zap` deducts the 0.75% Alt Fun fee (forwarded to `FeeVault`, split 0.5% protocol / 0.25% creator) — identical on curve and post-grad — and sends net USDC to the user in the same tx
   - Sell amount is limited by the LT's idle USDC buffer (`baseAssetBalance()`)
   - Frontend checks buffer and caps sell amounts; users sell in chunks if needed
   - BounceTech automation replenishes the buffer in ~10s after each redeem

```

**File:** packages/contracts/src/Zap.sol (L18-34)
```text
/// @title Zap
/// @notice User-facing entry point: pay USDC, receive tokens (and vice versa).
/// @dev Buy path: USDC → LT mint → curve buy (or V2 swap post-grad).
///      Sell path: token → curve sell or V2 swap → LT redeem → USDC.
///      Fee layer: every buy/sell skims USDC and forwards it to `FeeVault`. No
///      fees live on `Bonding`, `Router`, or `Factory`.
///      Permit variants apply an EIP-2612 sig before pulling funds; wrapped in
///      `try/catch` to defuse the standard permit-front-run DoS.
/// @dev Owner is the protocol multisig. Uses `Ownable2StepUpgradeable` so a
///      bad `transferOwnership` can be cancelled (or simply ignored by the
///      pending owner) before it takes effect — single-step transfer to a
///      fat-fingered or contract-incompatible address would otherwise brick
///      every owner-only path on the live proxy.
///
///      Storage uses ERC-7201 namespaced layout (no `__gap` needed). All
///      mutable state lives in `ZapStorage` at `_ZAP_STORAGE_LOCATION`.
contract Zap is UUPSUpgradeable, Ownable2StepUpgradeable, ReentrancyGuard {
```

**File:** packages/contracts/src/Bonding.sol (L1010-1025)
```text
        // Anything in this contract beyond `p.ltFromPair` belongs to a
        // concurrent graduation on the same LT (Phase 1 transferred it
        // via `Router.graduate`) or to stray dust. Either way it is
        // off-limits to this graduation's deposit and sweep — see
        // `_routerDepositAndDispose` and `_sweepLTToOwner`.
        // Saturating subtract: a balance below `p.ltFromPair` shouldn't
        // be reachable in normal operation, but we keep finalize from
        // bricking on a Panic if any future code path or non-canonical
        // LT briefly violates the invariant.
        uint256 ltBalance = IERC20(lt).balanceOf(address(this));
        uint256 protectedLT = ltBalance > p.ltFromPair ? ltBalance - p.ltFromPair : 0;

        address lpPair = _ensureUniswapV2Pair(tokenAddress, lt);
        uint256 liquidity = _seedUniswapV2Direct(tokenAddress, lt, lpPair, p.tokensForLP, p.ltFromPair, protectedLT);

        _sweepLTToOwner(lt, protectedLT);
```

**File:** packages/contracts/src/Bonding.sol (L1036-1052)
```text
    /// @dev Send LT held by this contract above `keep` to the owner,
    ///      emitting `LTRescued`. Called at the end of
    ///      `finalizeGraduation` with `keep = protectedLT` (any escrow
    ///      that doesn't belong to this graduation), so only THIS
    ///      graduation's rebalance residue lands on the owner. No-op on
    ///      the empty-pair fast path (nothing to sweep).
    function _sweepLTToOwner(
        address lt,
        uint256 keep
    ) internal {
        uint256 bal = IERC20(lt).balanceOf(address(this));
        if (bal <= keep) return;
        uint256 amount = bal - keep;
        address recipient = owner();
        IERC20(lt).safeTransfer(recipient, amount);
        emit LTRescued(lt, recipient, amount);
    }
```

**File:** packages/contracts/src/FeeVault.sol (L147-160)
```text
    /// @notice Sweep unbacked USDC (donations) to `feeTo`. Required because
    ///         direct USDC transfers would otherwise inflate `balanceOf` above
    ///         the accrual tally and silently mask the `accrue` underfund
    ///         check. Permissionless — funds always go to the admin-set `feeTo`.
    function sweepDonations() external nonReentrant returns (uint256 amount) {
        FeeVaultStorage storage $ = _s();
        uint256 backed = $.totalAccruedCreator + $.protocolBalance;
        uint256 balance = $.usdc.balanceOf(address(this));
        if (balance <= backed) revert NothingToClaim();
        amount = balance - backed;
        address feeTo_ = $.feeTo;
        $.usdc.safeTransfer(feeTo_, amount);
        emit DonationsSwept(feeTo_, amount);
    }
```
