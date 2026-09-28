### Title
Untracked tokens sent to the pool are permanently frozen — no sweep or credit path exists - (File: contracts/pool/src/cache/cash.rs)

### Summary
The pool tracks reserves in a bookkeeping `cash` counter rather than reading its real token balance. Any tokens transferred directly to the pool contract outside a controller-driven entrypoint are never credited to `cash`, and no entrypoint — owner or permissionless — can release them. This mirrors the FeeSplitter bug class (contract receives assets it cannot distribute), with native-XLM-or-any-SAC-token donations playing the role of stray ETH.

### Finding Description
`Cache::credit_cash` / `debit_cash` are the only mutators of accounting cash, and they are invoked only by pool ops (`supply`, `borrow`, `repay`, `flash_loan`, `recapitalize`, `seize_positions`, `claim_revenue`) — all `#[only_owner]` gated behind the controller. A direct `token.transfer(user → pool)` is in the unprivileged reach list but touches no bookkeeping. The README confirms the design: "`cash` is a bookkeeping number. The only reconciliation against a real `token.balance()` is in `flash_loan`" and "incidental token donations do not increase" cash. [1](#0-0) [2](#0-1) [3](#0-2) 

No outbound path can release the surplus:
- `transfer_out` only ever sends amounts already debited from `cash` [4](#0-3) 
- `claim_revenue` is capped at `min(cash, floor(revenue_value))` [5](#0-4) 
- `recapitalize` credits at most the backing shortfall and refunds the excess to the payer [6](#0-5) 
- `flash_loan`'s balance assertions use the live balance (`pre_balance` measured at call time), so donations neither get swept nor break the equality checks. [7](#0-6) 

There is no `sweep`/`rescue` entrypoint anywhere in the pool or controller ABI.

### Impact Explanation
Any tokens mistakenly or deliberately transferred directly to the pool contract are permanently locked: real `token.balance(pool) > cash` forever, and no code path can bridge that gap. This is permanent freezing of funds, matching the FeeSplitter impact (assets received but undistributable).

### Likelihood Explanation
Medium. Any token holder can send to a contract address with no auth barrier; accidental direct deposits to pool contracts are a recurring real-world pattern. The protocol itself mitigates nothing — unlike EVM pools, there is no skim/sync/donate mechanism to fold surplus into shares.

### Recommendation
Add an owner-gated `sweep(hub_asset)` / `sync` entrypoint that either (a) credits `token.balance(pool) - cash` as protocol revenue via `accrue_revenue` + `credit_cash`, or (b) transfers the surplus to the accumulator. Reusing `accrue_revenue` preserves the `revenue <= supplied` invariant.

### Proof of Concept
1. Attacker/user calls `token::Client(asset).transfer(user, pool_addr, amount)` directly — succeeds; `cash` unchanged.
2. `pool.get_reserves(hub_asset)` still returns pre-transfer `cash`; `token.balance(pool) > cash`.
3. `claim_revenue` via controller `claim_revenue(caller, vec![hub_asset])` pays only `min(cash, floor(revenue_value))` — donation untouched.
4. `recapitalize` credits only up to `backing_shortfall` and refunds the rest — cannot absorb the donation.
5. Donation remains locked permanently; no owner or permissionless entrypoint can move it.

### Citations

**File:** contracts/pool/src/cache/cash.rs (L24-41)
```rust
    pub(crate) fn credit_cash(&mut self, amount: i128) {
        require_nonneg_amount(&self.env, amount);
        self.cash = self
            .cash
            .checked_add(amount)
            .unwrap_or_else(|| panic_with_error!(&self.env, GenericError::MathOverflow));
    }

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

**File:** contracts/pool/src/cache/cash.rs (L46-53)
```rust
    pub(crate) fn transfer_out(&self, recipient: &Address, amount: i128) {
        require_nonneg_amount(&self.env, amount);
        if amount == 0 {
            return;
        }
        let tok = token::Client::new(&self.env, &self.params.asset_id);
        tok.transfer(&self.env.current_contract_address(), recipient, &amount);
    }
```

**File:** contracts/pool/README.md (L61-63)
```markdown
controller's word, without verifying the transfer. `cash` is a bookkeeping
number. The only reconciliation against a real `token.balance()` is in
`flash_loan`, which checks it three times with strict equality.
```

**File:** contracts/pool/README.md (L334-335)
```markdown
**`repay`** and **`recapitalize`** refund from pool cash without debiting it,
correct only because the controller transferred the full amount in first.
```

**File:** docs/reference/formulas.md (L76-82)
```markdown
## Cash, supply, debt, and revenue

Revenue is a supply-share claim included in total supplied shares. Revenue
minting increases both totals equally; claiming revenue burns both equally.
Reclassifying seized collateral as revenue leaves total supply unchanged.
Tracked cash is a separate reserve balance that incidental token donations do
not increase.
```

**File:** contracts/pool/src/cache/shares.rs (L54-65)
```rust
    pub(crate) fn burn_claimable_revenue(&mut self) -> i128 {
        let treasury_actual = self.unscale_supply_floor(self.revenue);
        let amount = self.cash.min(treasury_actual);
        if amount <= 0 {
            return 0;
        }
        let scaled_to_burn = if amount >= treasury_actual {
            self.revenue
        } else {
            self.revenue
                .mul_ratio_ceil(&self.env, amount, treasury_actual)
        };
```

**File:** contracts/pool/src/ops/flash.rs (L53-61)
```rust
    let terms = terms(
        env,
        amount,
        cache.params().flashloan_fee,
        asset.balance(&pool),
    );

    asset.transfer(&pool, &receiver, &amount);
    require_balance(env, &asset, &pool, terms.balance_after_payout);
```
