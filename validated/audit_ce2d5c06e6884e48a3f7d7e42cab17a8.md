### Title
`set_locked_tokens()` overwrites live accounting without old-value guard, enabling fund lock via TOCTOU race - (File: near/omni-bridge/src/token_lock.rs)

---

### Summary

`set_locked_tokens()` is a privileged correction function that blindly overwrites the `locked_tokens` mapping with an absolute value. Because `locked_tokens` is also mutated by the public user entry path (`ft_on_transfer` → `init_transfer_internal` → `lock_tokens_if_needed`), a user transaction that races with the admin's correction silently discards the user's delta. The resulting under-count causes every subsequent `unlock_tokens` call for that `(chain_kind, token_id)` pair to revert with `InsufficientLockedTokens`, permanently freezing the user's in-flight transfer.

---

### Finding Description

`set_locked_tokens` performs a raw `insert` with no read of the current value: [1](#0-0) 

The same storage slot is incremented atomically by `lock_tokens`, which is called from `init_transfer_internal` on every successful `ft_on_transfer`: [2](#0-1) 

`init_transfer_internal` calls `lock_tokens_if_needed` after the transfer message is stored: [3](#0-2) 

And `unlock_tokens` enforces a hard lower-bound check before releasing: [4](#0-3) 

Because NEAR transactions are ordered per-shard but two independent signers can submit concurrently, the following interleaving is reachable:

1. Admin reads `locked_tokens[(Eth, token)] = 1000` and decides to correct it to `900`.
2. User calls `ft_on_transfer` → `init_transfer_internal` → `lock_tokens`, atomically writing `1100`.
3. Admin's `set_locked_tokens` lands next, writing `900` — discarding the user's `+100`.
4. `locked_tokens[(Eth, token)]` is now `900`, but `1100` worth of tokens are actually locked.

When the user's transfer is later finalised on the destination chain and the relayer calls `fin_transfer_callback` → `process_fin_transfer_to_near` → `unlock_tokens_if_needed` → `unlock_tokens` with `amount = 100`, the check `available (900) >= amount (100)` passes — but if the admin correction was more aggressive (e.g., set to `50`), the check fails and the transfer is permanently stuck. [5](#0-4) 

---

### Impact Explanation

`locked_tokens` is the sole accounting gate for `unlock_tokens`. An under-count caused by the race makes `unlock_tokens` revert with `InsufficientLockedTokens` for every subsequent finalisation of a transfer whose delta was overwritten. The user's tokens are already locked in the bridge (transferred in via `ft_transfer_call`) but can never be released — a **Critical irreversible fund lock**.

An over-count (race in the opposite direction: user unlocks between admin's read and admin's write) inflates the counter, allowing future `unlock_tokens` calls to succeed even when the actual locked balance is lower, breaking the backing guarantee — a **Critical unauthorized release** path.

---

### Likelihood Explanation

`set_locked_tokens` is explicitly used during operational corrections (e.g., BTC storage-fix migration in tests calls it to reset a counter to `0` while the bridge is live). Any user who submits an `ft_on_transfer` in the same block window as an admin correction triggers the race. No special knowledge or coordination is required from the user — normal bridge usage suffices.

---

### Recommendation

Add an `expected_amount` field to `SetLockedTokenArgs` and assert it matches the current value before overwriting:

```rust
pub fn set_locked_tokens(&mut self, args: Vec<SetLockedTokenArgs>) {
    for arg in args {
        let key = (arg.chain_kind, arg.token_id.clone());
        let current = self.locked_tokens.get(&key).unwrap_or(0);
        require!(
            current == arg.expected_amount.0,
            "ERR_LOCKED_TOKENS_STALE_EXPECTED_AMOUNT"
        );
        self.locked_tokens.insert(&key, &arg.amount.0);
    }
}
```

This is the direct analog of the mitigation recommended in the external report (adding `oldBalance` and reverting on mismatch).

---

### Proof of Concept

```
locked_tokens[(Eth, usdc.near)] = 1_000_000

1. Admin observes 1_000_000, decides to correct to 900_000.
   Admin submits: set_locked_tokens([{Eth, usdc.near, 900_000}])

2. Alice submits ft_transfer_call(bridge, 200_000, InitTransfer{recipient: Eth:0xAlice})
   → lock_tokens_if_needed(Eth, usdc.near, 200_000)
   → locked_tokens[(Eth, usdc.near)] = 1_200_000   ← lands first (higher gas)

3. Admin tx lands:
   → locked_tokens[(Eth, usdc.near)] = 900_000      ← Alice's +200_000 erased

4. Alice's transfer is signed by MPC and relayer calls fin_transfer_callback
   → unlock_tokens(Eth, usdc.near, 200_000)
   → require!(900_000 >= 200_000) — passes here, but if admin set 50_000:
   → require!(50_000 >= 200_000) — PANICS → Alice's 200_000 USDC permanently locked
``` [1](#0-0) [6](#0-5)

### Citations

**File:** near/omni-bridge/src/token_lock.rs (L38-44)
```rust
    #[access_control_any(roles(Role::DAO, Role::TokenLockController))]
    pub fn set_locked_tokens(&mut self, args: Vec<SetLockedTokenArgs>) {
        for arg in args {
            self.locked_tokens
                .insert(&(arg.chain_kind, arg.token_id), &arg.amount.0);
        }
    }
```

**File:** near/omni-bridge/src/token_lock.rs (L48-68)
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
```

**File:** near/omni-bridge/src/token_lock.rs (L71-87)
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
```

**File:** near/omni-bridge/src/lib.rs (L1855-1866)
```rust
        if let OmniAddress::Near(token_id) = transfer_message.token.clone() {
            self.burn_tokens_if_needed(token_id.clone(), transfer_message.amount);

            self.lock_tokens_if_needed(
                transfer_message.get_destination_chain(),
                &token_id,
                transfer_message.amount.0,
            );
        } else {
            self.remove_transfer_message_without_refund(transfer_message.get_transfer_id());
            return transfer_message.amount;
        }
```

**File:** near/omni-bridge/src/lib.rs (L1886-1890)
```rust
        let lock_actions = vec![self.unlock_tokens_if_needed(
            transfer_message.get_origin_chain(),
            &token,
            transfer_message.amount.0,
        )];
```
