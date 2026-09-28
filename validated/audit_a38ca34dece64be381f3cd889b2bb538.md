### Title
No rescue path for tokens held by the pool/controller — stray balances are permanently locked - (File: contracts/pool/src/lib.rs)

### Summary
The `LiquidityPool` contract tracks `cash` as a pure accounting book decoupled from its real token balance, and exposes no entrypoint to recover balances that exceed the accounted cash. Every mutator is `#[only_owner]`-gated to the controller, and the controller exposes no sweep/rescue either. Any tokens that arrive at the pool address outside the accounted paths (direct user transfers, accidental transfers, airdrops) are permanently unrecoverable — the same broken-rescue class as the reference report, where `rescueTokens` existed but was unreachable; here the capability does not exist at all.

### Finding Description
The pool's header explicitly states: "Cash is an accounting book, separate from the token balance" ( [1](#0-0) ). All outflows are bounded by accounted state:

- `withdraw` burns supply shares and pays out only up to booked `cash` ( [2](#0-1) ).
- `claim_revenue` pays `min(cash, revenue)` — again cash-bounded ( [3](#0-2) ).
- `recapitalize` is the only function that even notices raw token inflows, and it credits `min(amount, backing_shortfall)` to cash and transfers the remainder back to `payer` — it cannot absorb an unaccounted surplus that already sits in the contract, and it is owner-only ( [4](#0-3) ).

A repo-wide search for `sweep|rescue|recover` finds an implementation only in `contracts/swap-aggregator/src/lib.rs` (`sweep_balance`), which is out of scope. The pool and controller have no equivalent: every mutator on `LiquidityPool` is `#[only_owner]` (owner = controller, INV-AUTH-01), and the controller's own function surface contains no stray-balance recovery entrypoint. So there is no authorized caller chain — controller or governance — that can move tokens above the cash book out of the pool.

Attack/reachability path (allowed by scope): any unprivileged address performs a direct `token.transfer(from: self, to: pool, amount)`. The pool's real balance rises but `cash`, `total_supply`, and `revenue` are unchanged; no subsequent `supply`, `repay`, `withdraw`, `claim_revenue`, or `recapitalize` call by anyone will ever distribute or extract that surplus.

### Impact Explanation
Permanent freezing of funds. Tokens transferred directly to the pool contract are locked forever — they do not accrue to suppliers (supply shares were never minted), do not accrue to protocol revenue, and cannot be withdrawn because all payouts are capped by the internal `cash` book. If a user (or a third-party integration, or a mistaken refund) sends market tokens to the pool, those tokens are burned in practice. More importantly, in a bad-debt/insolvency scenario the protocol has no mechanism to inject or claw back liquidity: `recapitalize` only fixes `backing_shortfall` up to the accounted gap and refunds everything above it, so even the admin cannot deliberately over-fund the pool to restore solvency headroom.

### Likelihood Explanation
Direct token transfers to contract addresses are a routine real-world occurrence (mistaken sends, integrations pushing refunds, leftover tokens after a `transfer` in multi-call flows). Because the outcome requires only a plain token transfer — an action explicitly in the reachable set — the trigger is trivially reachable by any unprivileged address, though it requires funds to be sent to the contract in the first place. The absence of any rescue path is deterministic, not probabilistic.

### Recommendation
Add an owner-gated `sweep`/`rescue` on the pool (mirroring the swap-aggregator's `sweep_balance`) that transfers `balance - cash_backing` for a token to a recipient, where `cash_backing` is computed from the market's cash book. Alternatively, expose a controller-level `rescue_tokens(token, receiver, amount)` that instructs the pool to pay out strictly the unaccounted surplus, routed through governance. Ensure the sweep can never touch accounted cash, supply-share backing, or accrued revenue.

### Proof of Concept
1. Pool market `(hub, USDC)` exists with `cash = C` and token balance `= C` (fully backed, no borrows for simplicity).
2. Attacker/victim calls `USDC.transfer(victim, pool, 10_000)`.
3. `get_reserves(hub_usdc)` still returns `C`; `get_revenue` unchanged; no shares minted.
4. Withdraw all supply → pool receives `C` out, balance falls to `10_000`.
5. Call every owner entrypoint (`claim_revenue`, `recapitalize`, `withdraw`, `net_settle`, `flash_loan`): none can emit more than accounted cash/revenue; `recapitalize` refunds excess rather than absorbing it.
6. Result: `10_000` USDC remains on the pool address with no code path able to move it — permanently frozen, exactly the stranded-asset impact of the reference `rescueTokens` report.

Note: the controller source was only partially surveyed (function list grep, not full read); the conclusion rests on the complete pool entrypoint surface in `lib.rs` plus the repo-wide absence of any `sweep`/`rescue`/`recover` implementation outside the out-of-scope swap-aggregator.

### Citations

**File:** contracts/pool/src/lib.rs (L34-36)
```rust
//! - Cash is an accounting book, separate from the token balance. A flash loan
//!   checks the token balance after payout, after the callback and after
//!   repayment.
```

**File:** contracts/pool/src/lib.rs (L150-163)
```rust
    /// Burns supply shares and transfers the underlying to `receiver`.
    /// `is_liquidation` skips the max-utilization check and may withhold a
    /// protocol fee. Owner-only; `actual_amount` is gross of that fee.
    #[only_owner]
    fn withdraw(
        env: Env,
        receiver: Address,
        is_liquidation: bool,
        entries: Vec<PoolWithdrawEntry>,
    ) -> Vec<PoolPositionMutation> {
        ops::run_batch(&env, entries, |env, entry| {
            ops::withdraw::apply(env, &receiver, is_liquidation, entry)
        })
    }
```

**File:** contracts/pool/src/lib.rs (L243-252)
```rust
    /// Burns claimable revenue shares, debits cash and pays the owner the lesser
    /// of cash and revenue's floored token value. Returns zero when nothing is
    /// claimable. Owner-only.
    ///
    /// Decrements the snapshot `revenue` field, so that field is not a
    /// cumulative counter.
    #[only_owner]
    fn claim_revenue(env: Env, hub_asset: HubAssetKey) -> PoolAmountMutation {
        ops::revenue::apply(&env, hub_asset)
    }
```

**File:** contracts/pool/src/ops/recapitalize.rs (L52-58)
```rust
    let applied = amount.min(guards::backing_shortfall(&cache));
    let refund = amount
        .checked_sub(applied)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

    cache.credit_cash(applied);
    cache.commit();
```
