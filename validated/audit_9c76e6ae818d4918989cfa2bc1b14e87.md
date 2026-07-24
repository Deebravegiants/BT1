### Title
Silent Skip of Locked-Balance Accounting When `locked_tokens` Entry Is Absent — (`near/omni-bridge/src/token_lock.rs`)

### Summary
Both `lock_tokens` and `unlock_tokens` in the NEAR bridge silently return `LockAction::Unchanged` when the `locked_tokens` map has no entry for a given `(chain_kind, token_id)` key. Because `locked_tokens` entries are only initialized for the specific chain/token pair at `bind_token` time, any transfer involving an uninitialized chain/token pair bypasses the locked-balance check entirely, breaking the backing guarantee.

### Finding Description

`lock_tokens` (lines 55–56) and `unlock_tokens` (lines 78–79) both use an early-return pattern when the map key is absent:

```rust
// lock_tokens
let Some(current_amount) = self.locked_tokens.get(&key) else {
    return LockAction::Unchanged;   // silently skips — no entry created
};
```

```rust
// unlock_tokens
let Some(available) = self.locked_tokens.get(&key) else {
    return LockAction::Unchanged;   // silently skips — ERR_INSUFFICIENT_LOCKED_TOKENS never fires
};
```

The only place that initializes a `locked_tokens` entry is `bind_token_callback` (lines 1273–1284), which inserts `0` for exactly one `(chain, token)` pair — the chain of the token address in the `DeployToken` proof:

```rust
self.locked_tokens.insert(
    &(deploy_token.token_address.get_chain(), deploy_token.token.clone()),
    &0,
)
```

No entry is created for any other chain. Consequently:

- `lock_tokens_if_needed` called during `init_transfer_internal` for a destination chain that has no entry silently skips — tokens are burned on NEAR but the destination-chain locked counter is never incremented.
- `unlock_tokens_if_needed` called during `process_fin_transfer_to_near` (and `process_fin_transfer_to_other_chain`) for an origin chain that has no entry silently skips — the `ERR_INSUFFICIENT_LOCKED_TOKENS` guard is never reached, and tokens are minted or forwarded without any backing verification.

The existing unit test `test_fin_transfer_callback_near_fails_without_locked_tokens` confirms the guard fires only when the entry *exists* with an insufficient value; it does not cover the absent-entry path, which silently succeeds.

### Impact Explanation

When `locked_tokens[(origin_chain, token)]` is absent, `fin_transfer` to NEAR mints tokens to the recipient without verifying that any corresponding amount was locked on the origin chain. This breaks the core backing invariant: the NEAR bridge's locked-balance ledger no longer constrains how many tokens can be released. Any token/chain pair that was registered through a code path that does not call `bind_token_callback` (e.g., `deploy_token_internal`, `set_locked_tokens` omission, or future migration paths) is permanently unguarded. This constitutes balance-accounting divergence that breaks backing guarantees.

### Likelihood Explanation

The condition is reachable whenever a token is registered in the bridge (present in `token_address_to_id` and `token_decimals`) but its `locked_tokens` entry for the relevant chain was never seeded. This occurs for every chain/token combination beyond the single pair initialized by `bind_token_callback`, including cross-chain routing paths (e.g., Eth-origin token routed to Sol) and any token registered via `deploy_token_internal` if that function omits the `locked_tokens.insert` call. An unprivileged user triggers the path simply by calling `ft_transfer_call` → `init_transfer` or by being the recipient of a `fin_transfer`.

### Recommendation

1. In `lock_tokens`, treat a missing entry as `0` and insert it rather than returning `Unchanged`:
   ```rust
   let current_amount = self.locked_tokens.get(&key).unwrap_or(0);
   ```
2. In `unlock_tokens`, treat a missing entry as `0` so the `require!(available >= amount)` guard fires correctly instead of silently passing.
3. Audit every token-registration path (`deploy_token_internal`, migration, `add_utxo_chain_connector`) to ensure each one seeds a `locked_tokens` entry of `0` for every chain the token will be transferred to or from.

### Proof of Concept

1. Token `T` is registered for Eth via `bind_token` → `locked_tokens[(Eth, T)] = 0` is seeded.
2. Token `T` is also reachable on Sol (e.g., via `deploy_token` if `deploy_token_internal` omits the `locked_tokens.insert` call) → `locked_tokens[(Sol, T)]` does **not** exist.
3. A user legitimately locks `N` tokens on Sol and the MPC signs the transfer.
4. Relayer calls `fin_transfer` on NEAR; `fin_transfer_callback` → `process_fin_transfer_to_near`.
5. `unlock_tokens_if_needed(Sol, T, N)` → `unlock_tokens` → `locked_tokens.get(&(Sol, T))` returns `None` → returns `LockAction::Unchanged` silently.
6. `N` tokens are minted to the recipient on NEAR with **no locked-balance check performed**.
7. The NEAR bridge's backing ledger for Sol is permanently untracked; any future over-issuance from Sol goes undetected at the NEAR layer. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** near/omni-bridge/src/token_lock.rs (L48-69)
```rust
    fn lock_tokens(
        &mut self,
        chain_kind: ChainKind,
        token_id: &AccountId,
        amount: u128,
    ) -> LockAction {
        let key = (chain_kind, token_id.clone());
        let Some(current_amount) = self.locked_tokens.get(&key) else {
            return LockAction::Unchanged;
        };
        let new_amount = current_amount
            .checked_add(amount)
            .near_expect(TokenLockError::LockedTokensOverflow);

        self.locked_tokens.insert(&key, &new_amount);

        LockAction::Locked {
            chain_kind,
            token_id: token_id.clone(),
            amount,
        }
    }
```

**File:** near/omni-bridge/src/token_lock.rs (L71-94)
```rust
    fn unlock_tokens(
        &mut self,
        chain_kind: ChainKind,
        token_id: &AccountId,
        amount: u128,
    ) -> LockAction {
        let key = (chain_kind, token_id.clone());
        let Some(available) = self.locked_tokens.get(&key) else {
            return LockAction::Unchanged;
        };
        require!(
            available >= amount,
            TokenLockError::InsufficientLockedTokens.as_ref()
        );

        let remaining = available - amount;
        self.locked_tokens.insert(&key, &remaining);

        LockAction::Unlocked {
            chain_kind,
            token_id: token_id.clone(),
            amount,
        }
    }
```

**File:** near/omni-bridge/src/token_lock.rs (L96-107)
```rust
    pub(crate) fn lock_tokens_if_needed(
        &mut self,
        chain_kind: ChainKind,
        token_id: &AccountId,
        amount: u128,
    ) -> LockAction {
        if self.get_token_origin_chain(token_id) == chain_kind || amount == 0 {
            return LockAction::Unchanged;
        }

        self.lock_tokens(chain_kind, token_id, amount)
    }
```

**File:** near/omni-bridge/src/token_lock.rs (L109-120)
```rust
    pub(crate) fn unlock_tokens_if_needed(
        &mut self,
        chain_kind: ChainKind,
        token_id: &AccountId,
        amount: u128,
    ) -> LockAction {
        if self.get_token_origin_chain(token_id) == chain_kind || amount == 0 {
            return LockAction::Unchanged;
        }

        self.unlock_tokens(chain_kind, token_id, amount)
    }
```

**File:** near/omni-bridge/src/lib.rs (L1273-1284)
```rust
        require!(
            self.locked_tokens
                .insert(
                    &(
                        deploy_token.token_address.get_chain(),
                        deploy_token.token.clone(),
                    ),
                    &0,
                )
                .is_none(),
            TokenLockError::TokenAlreadyLocked.as_ref()
        );
```
