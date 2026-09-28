### Title
Direct token transfers to the pool permanently strand unbooked assets - (File: contracts/pool/src/cache/cash.rs)

### Summary
An unprivileged user can send a listed token directly to the pool's Stellar Asset Contract address. The pool deliberately tracks only its internal `cash` book and does not credit unsolicited balance increases. Since outbound transfers are limited to bookkeeping flows and neither the pool nor controller exposes a stray-balance recovery path, the donated amount remains permanently unclaimable. [1](#0-0) 

### Finding Description
Pool liquidity checks and accounting use `Cache.cash`, not the token contract's live balance. `debit_cash` permits an outbound amount only when tracked cash is sufficient, while `transfer_out` separately moves tokens without reconciling the pool's actual balance. [2](#0-1) [3](#0-2) 

A direct `token.transfer(user, pool, amount)` therefore increases only the physical token balance. It does not increase `cash`, mint supply shares, create revenue, or record the sender as a creditor. The repository's money-flow regression test explicitly verifies that a seven-token unsolicited transfer remains outside every market's cash book. [1](#0-0) 

The pool's token-moving operations—supply, borrow, withdraw, repay, recapitalize, revenue claims, flash loans, and strategy creation—are owner-only accounting operations invoked by the controller; none provides a general surplus sweep. [4](#0-3) [5](#0-4) 

Controller paths that use token balances intentionally snapshot the balance and operate only on the positive delta produced during the operation, preserving any pre-existing controller or pool balance rather than attributing it to the caller. [6](#0-5) 

### Impact Explanation
The sender's transferred tokens are permanently frozen. They cannot be withdrawn as collateral because no shares or cash credit were issued, cannot be borrowed because pool borrowing is bounded by tracked `cash`, and cannot be recovered by a dedicated pool or controller entrypoint. [7](#0-6) 

The stranded balance also does not become protocol revenue or recapitalization funding: backing calculations and reserve checks use tracked books rather than the surplus SAC balance. [8](#0-7) [9](#0-8) 

This matches the reported bug class on Soroban: an asset sent to the protocol contract outside an accounting-aware deposit path is accepted by the token contract but is unreachable by the protocol's own withdrawal logic.

### Likelihood Explanation
Likelihood is limited because exploitation requires a user or integration to transfer tokens directly to the pool address rather than calling `Controller::supply`. No attacker can force an arbitrary victim to make that transfer. However, the action is permissionless, requires no special privileges or race condition, and any mistaken integration or manually constructed token transfer permanently creates the condition. The resulting loss can be the full transferred amount.

### Recommendation
Add an explicit surplus-handling path for pool balances above the aggregate tracked cash across all markets sharing the same token. At minimum, governance should be able to sweep only `token.balance(pool) - aggregate_booked_cash`, never booked reserves. A preferable design would expose a controlled donation/recapitalization entrypoint that either credits an intended account or books the amount as protocol revenue, while rejecting plain integrations that mistakenly use direct token transfers.

If rescue authority is intentionally excluded, the contract cannot prevent SAC transfers to its address, so this behavior should be surfaced prominently to integrators and enforced in client transaction builders.

### Proof of Concept
```rust
// Any listed market asset and its corresponding pool address.
let hub_asset = HubAssetKey { hub_id, asset };
let pool = controller.pool_for(hub_asset);
let token = token::Client::new(&env, &asset);

let cash_before = pool.get_reserves(&hub_asset);
let balance_before = token.balance(&pool);

// Permissionless path: transfer directly to the pool instead of calling supply.
token.transfer(&victim, &pool, &amount);

// The physical balance increases, but no market book, shares, revenue,
// or debt backing changes.
assert_eq!(token.balance(&pool), balance_before + amount);
assert_eq!(pool.get_reserves(&hub_asset), cash_before);

// There is no permissionless or owner-callable pool entrypoint that releases
// balance above the aggregate book. Borrow and withdraw remain bounded by
// `cash`, so `amount` remains stranded after every booked claim is paid.
```

The existing test already demonstrates the accounting state after such a transfer: the token balance equals both markets' booked cash plus the unsolicited seven-token amount. [1](#0-0)

### Citations

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

**File:** contracts/pool/src/cache/cash.rs (L14-20)
```rust
    /// Panics if cash reserves are below `amount`.
    pub(crate) fn require_reserves(&self, amount: i128) {
        assert_with_error!(
            self.env,
            self.cash >= amount,
            CollateralError::InsufficientLiquidity
        );
```

**File:** contracts/pool/src/cache/cash.rs (L32-41)
```rust
    /// Decreases accounting cash by `amount`. Rejects negative amounts or
    /// insufficient reserves.
    pub(crate) fn debit_cash(&mut self, amount: i128) {
        require_nonneg_amount(&self.env, amount);
        self.require_reserves(amount);
        self.cash = self
            .cash
            .checked_sub(amount)
            .unwrap_or_else(|| panic_with_error!(&self.env, GenericError::MathOverflow));
    }
```

**File:** contracts/pool/README.md (L71-82)
```markdown
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

**File:** contracts/controller/src/payments.rs (L39-50)
```rust
/// Refunds only the controller balance increase since `balance_before`,
/// preserving the pre-existing balance; no-op for a nonpositive delta.
pub(crate) fn refund_controller_balance_delta(
    env: &Env,
    asset: &Address,
    balance_before: i128,
    refund_to: &Address,
) {
    let controller = env.current_contract_address();
    let excess = balance_delta_since(env, asset, &controller, balance_before);
    if excess > 0 {
        token::Client::new(env, asset).transfer(&controller, refund_to, &excess);
```

**File:** contracts/pool/src/ops/borrow.rs (L63-67)
```rust
pub(crate) fn mint_debt(env: &Env, cache: &mut Cache, position: &mut Ray, amount: i128) {
    require_positive_amount(env, amount);
    cache.require_reserves(amount);
    guards::require_liquidation_buffer(env, cache, amount);

```

**File:** docs/reference/formulas.md (L76-83)
```markdown
## Cash, supply, debt, and revenue

Revenue is a supply-share claim included in total supplied shares. Revenue
minting increases both totals equally; claiming revenue burns both equally.
Reclassifying seized collateral as revenue leaves total supply unchanged.
Tracked cash is a separate reserve balance that incidental token donations do
not increase.

```

**File:** docs/reference/invariants.md (L104-109)
```markdown
### INV-ACCT-02 — Cash is the reserve book

Reserve checks use tracked market cash; token donations alone do not increase
it. Cash credits and debits reject negative amounts. Credits reject overflow,
and debits reject insufficient reserves. Outbound token transfer and cash
bookkeeping remain separate actions.
```
