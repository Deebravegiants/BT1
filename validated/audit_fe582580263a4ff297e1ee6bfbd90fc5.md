### Title
Tokens pushed directly to the pool or controller are permanently stranded — no sweep or donation-credit path exists - ([File: contracts/controller/src/positions/supply.rs](contracts/controller/src/positions/supply.rs))

### Summary
The Nested M-03 pattern is "value arrives alongside a call but is never credited, so it is locked forever." On Soroban there is no `msg.value`, but the same class exists for pushed ERC-20/SAC tokens: every credit-granting path in XOXNO Lending uses `transfer_amount_measured`, which only credits the balance delta produced *during* its own `token.transfer` call. Tokens that land on the pool or controller outside such a call are invisible to every book (`cash`, supply shares, revenue) and there is no sweep, skim, or rescue entrypoint on either contract to release them.

### Finding Description
`common::token::transfer_amount_measured` snapshots `balance(to)` immediately before and after the pull and credits only `post - pre`, so any pre-existing surplus at the recipient is never captured. [1](#0-0)  All user-facing inflows go through this helper — e.g., `process_deposit` measures the caller→pool delta per leg and nothing else. [2](#0-1) 

On the pool side, accounting is purely book-based: INV-ACCT-02 states "Reserve checks use tracked market cash; token donations alone do not increase it," and the harness test `pool_all_money_paths_preserve_books_and_shared_token_custody` confirms a direct `token.transfer(payer, pool, 7*UNIT)` is only observable as `balance(pool) == cash + donation`, never entering `cash`. [3](#0-2) [4](#0-3) 

Because every outflow is gated by tracked `cash` (`borrow`/`withdraw`/`claim_revenue` revert on `InsufficientLiquidity`/bounds) and `recapitalize` only credits up to the book shortfall (not the balance surplus), a stranded surplus can never be released to anyone. [5](#0-4)  The controller has the same hole: `flash_position` callback receipts that are in neither the collateral declarations nor the refund list "remain uncredited" and "there is no controller sweep endpoint." [6](#0-5) 

### Impact Explanation
Permanent freezing of funds. A user (or a composable wrapper contract, which the SDK explicitly supports for sequencing calls) that pushes tokens to the pool/controller — or a `flash_position` receiver that returns an undeclared asset — loses those tokens irrecoverably; they inflate `token.balance(pool)` above `cash` forever and benefit no one, since no book, share, or admin claim can touch them. [3](#0-2) 

### Likelihood Explanation
Medium/low, mirroring M-03: it requires user error rather than an attacker. However, the composed-call design (wrappers authorizing exact `transfer` trees per leg) makes misdirected pushes plausible, and `flash_position`'s callback lets any returned-but-undeclared asset fall into the gap. Once sent, the loss is total and unrecoverable by design — there is no privileged escape hatch either. [6](#0-5) 

### Recommendation
Add an owner-gated sweep on the pool that transfers only `token.balance(pool) - sum(cash over all books sharing that pool)` for a given asset, and a controller sweep restricted to assets with no accounting claim (excluding assets currently custodied for in-flight operations). At minimum, document prominently that pushed transfers are burned, and have `flash_position` refunds default unlisted positive receipts to the caller rather than stranding them. [7](#0-6) 

### Proof of Concept
1. `token.transfer(user, pool, X)` directly on a listed asset's pool address.
2. `get_reserves(hub_asset)` still returns the old `cash`; `token.balance(pool)` is `cash + X`.
3. No entrypoint (`borrow`, `withdraw`, `claim_revenue`, `recapitalize`) can release the `X` — all are bounded by tracked `cash`, and the pool ABI has no sweep. [8](#0-7) 
4. Same outcome on the controller: a `flash_position` receiver returns an asset not declared as collateral or refund; the measured-receipt logic ignores it and it sits on the controller permanently. [6](#0-5)

### Citations

**File:** common/src/token.rs (L16-31)
```rust
pub fn transfer_amount_measured(
    env: &Env,
    asset: &Address,
    from: &Address,
    to: &Address,
    amount: i128,
    non_positive_error: GenericError,
) -> i128 {
    assert_with_error!(env, amount > 0, non_positive_error);
    let tok = token::Client::new(env, asset);
    let pre = tok.balance(to);
    tok.transfer(from, to, &amount);
    let post = tok.balance(to);
    post.checked_sub(pre)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::AmountMustBePositive))
}
```

**File:** contracts/controller/src/positions/supply.rs (L116-130)
```rust
    for (hub_asset, amount_in) in aggregated.iter() {
        let asset_config: AssetConfig = cache.require_spoke_asset(account.spoke_id, &hub_asset);
        let received = payments::transfer_amount_measured(
            env,
            &hub_asset.asset,
            caller,
            &pool_addr,
            amount_in,
            GenericError::AmountMustBePositive,
        );
        let position = account.get_or_create_supply_position(&hub_asset, &asset_config);
        entries.push_back(PoolSupplyEntry {
            action: make_pool_action(&position, received, hub_asset.clone()),
        });
    }
```

**File:** docs/reference/invariants.md (L104-109)
```markdown
### INV-ACCT-02 — Cash is the reserve book

Reserve checks use tracked market cash; token donations alone do not increase
it. Cash credits and debits reject negative amounts. Credits reject overflow,
and debits reject insufficient reserves. Outbound token transfer and cash
bookkeeping remain separate actions.
```

**File:** tests/test-harness/tests/pool_money_flow_audit.rs (L86-96)
```rust
    // An unsolicited donation belongs to no market's cash book.
    market.token_admin.mint(&payer, &(7 * UNIT));
    token.transfer(&payer, &market.pool, &(7 * UNIT));
    let check = |supply, debt, label: &str| {
        let state = books(&t, &key, supply, debt);
        let other = books(&t, &second, secondary_supply, 0);
        assert_eq!(other.cash, 100 * UNIT);
        assert_eq!(
            token.balance(&market.pool),
            state.cash + other.cash + 7 * UNIT
        );
```

**File:** contracts/pool/README.md (L59-63)
```markdown
`swap_collateral` and `repay_debt_with_collateral`. The last row is the
load-bearing one: `supply`, `repay` and `recapitalize` all credit `cash` on the
controller's word, without verifying the transfer. `cash` is a bookkeeping
number. The only reconciliation against a real `token.balance()` is in
`flash_loan`, which checks it three times with strict equality.
```

**File:** contracts/pool/README.md (L66-88)
```markdown

| Entrypoint | Role | Tokens |
| --- | --- | --- |
| `create_market` | Verify params, write state, indexes at `RAY` | — |
| `update_params` | Accrue on the **old** curve, then replace the rate model | — |
| `update_indexes` | Accrue each market in the vec; commit only if time elapsed | — |
| `supply` | Mint supply shares, credit cash | in |
| `borrow` | Mint debt shares, debit cash, transfer | out |
| `withdraw` | Burn supply shares, withhold liquidation fee, transfer net | out |
| `repay` | Burn debt shares, credit net, refund overpayment | in/out |
| `net_settle` | Offset a user's own supply against their own debt | — |
| `seize_positions` | Bad-debt write-down, or deposit → revenue | — |
| `claim_revenue` | Burn revenue shares, transfer to owner | out |
| `recapitalize` | Credit cash up to the backing shortfall, refund excess | in/out |
| `flash_loan` | Payout → callback → collect principal + fee | out/in |
| `create_strategy` | Borrow for a strategy, net of fee | out |
| `upgrade` | Replace contract Wasm | — |

Tokens column: `in` means the controller transferred to the pool before the
call and the pool only credits `cash`; `out` means the pool transfers. `in/out`
is an inbound amount with an outbound refund leg — `repay` returns
overpayment, `recapitalize` returns whatever exceeded the shortfall.
`flash_loan` is `out/in`: principal leaves, then principal plus fee returns.
```

**File:** contracts/pool/README.md (L105-114)
```markdown
| `supply` | `fn supply(env: Env, entries: Vec<PoolSupplyEntry>) -> Vec<PoolPositionMutation>` | owner | Mints supply shares and credits cash, one mutation returned per entry. |
| `borrow` | `fn borrow(env: Env, receiver: Address, entries: Vec<PoolBorrowEntry>) -> Vec<PoolPositionMutation>` | owner | Mints debt shares, debits cash, and transfers the asset to `receiver`. |
| `withdraw` | `fn withdraw(env: Env, receiver: Address, is_liquidation: bool, entries: Vec<PoolWithdrawEntry>) -> Vec<PoolPositionMutation>` | owner | Burns supply shares and transfers the net amount to `receiver`. |
| `repay` | `fn repay(env: Env, payer: Address, actions: Vec<PoolAction>) -> Vec<PoolPositionMutation>` | owner | Burns debt shares, credits the net repay, and refunds overpayment to `payer`. |
| `net_settle` | `fn net_settle(env: Env, entry: PoolNetSettleEntry) -> PoolNetSettleResult` | owner | Offsets one user's supply against their own debt. Takes one entry, not a batch. |
| `seize_positions` | `fn seize_positions(env: Env, entries: Vec<PoolSeizeEntry>)` | owner | Writes off bad debt on the borrow side, or books a seized deposit as revenue. Returns nothing. |
| `flash_loan` | `fn flash_loan(env: Env, hub_asset: HubAssetKey, initiator: Address, receiver: Address, amount: i128, data: Bytes) -> i128` | owner | Pays out, calls `execute_flash_loan` on `receiver`, pulls principal plus fee back. Returns the fee. |
| `create_strategy` | `fn create_strategy(env: Env, receiver: Address, action: PoolAction, charge_fee: bool) -> PoolStrategyMutation` | owner | Mints debt, books the optional fee as revenue, and sends `amount - fee` to `receiver`. |
| `recapitalize` | `fn recapitalize(env: Env, hub_asset: HubAssetKey, payer: Address, amount: i128) -> PoolAmountMutation` | owner | Credits cash up to the backing shortfall and refunds the excess to `payer`. |
| `claim_revenue` | `fn claim_revenue(env: Env, hub_asset: HubAssetKey) -> PoolAmountMutation` | owner | Burns revenue shares and transfers the proceeds to the owner. |
```

**File:** docs/reference/endpoints.md (L84-86)
```markdown
Refund assets must be unique, listed in the debt hub and account spoke, disjoint from collateral declarations, and bounded by the maximum supply-position count. Refund eligibility requires an active spoke and an existing listing; it does not check collateralizable, borrowable, paused or frozen flags. Only positive balance changes above pre-callback balances return to the caller. The debt token can be a refund asset, but refunding it does not repay the minted debt.

Undeclared callback assets receive neither credit nor refunds. There is no controller sweep endpoint. Refunds produce token transfer events, without a dedicated controller refund event.
```
