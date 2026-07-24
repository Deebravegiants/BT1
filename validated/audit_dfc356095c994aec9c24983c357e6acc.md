### Title
`migrate_deployed_token` Leaves In-Flight Pending Transfers Permanently Unresolvable — (`near/omni-bridge/src/lib.rs`)

### Summary
`migrate_deployed_token` atomically re-keys the token address mappings from `old_token` to `new_token` but does not touch `pending_transfers` or `locked_tokens`. Any outbound transfer that was created before the migration and is still awaiting `sign_transfer` will panic permanently when the relayer attempts to sign it, because the `token_id_to_address` entry for `old_token` no longer exists. The user's tokens are locked inside the bridge with no cancel or refund path.

### Finding Description

`migrate_deployed_token` performs the following state changes: [1](#0-0) 

It removes `token_id_to_address[(origin_chain, old_token)]` and inserts `token_id_to_address[(origin_chain, new_token)]`. It also records `migrated_tokens[old_token] = new_token`.

What it does **not** do:
- Scan or cancel `pending_transfers` entries that carry `token: OmniAddress::Near(old_token)`.
- Migrate `locked_tokens[(chain_kind, old_token)]` to `locked_tokens[(chain_kind, new_token)]`.

When a user initiates an outbound transfer, `init_transfer` stores the NEAR token account ID directly in the `TransferMessage`: [2](#0-1) 

The relayer later calls `sign_transfer`, which resolves the destination-chain token address: [3](#0-2) 

`get_token_id` for `OmniAddress::Near(old_token)` returns `old_token` directly without any migration lookup: [4](#0-3) 

After migration, `token_id_to_address.get(&(destination_chain, old_token))` returns `None`, causing an unconditional panic via `env::panic_str(BridgeError::FailedToGetTokenAddress)`. There is no public cancel or refund function for `pending_transfers`; the only removal paths are through `sign_transfer_callback` (unreachable if `sign_transfer` panics) and `claim_fee` (requires a proof from the destination chain that the transfer was finalised, which it never was).

The `locked_tokens` map is also not migrated: [5](#0-4) 

After migration, `locked_tokens[(chain_kind, old_token)]` still holds the pre-migration balance. New transfers using `new_token` call `lock_tokens_if_needed(chain_kind, new_token, amount)`, which silently returns `LockAction::Unchanged` because `locked_tokens.get(&(chain_kind, new_token))` is `None`: [6](#0-5) 

This breaks the locked-token accounting for all future transfers of the migrated token.

### Impact Explanation
**Critical — Irreversible fund lock.** Tokens transferred to the bridge via `ft_transfer_call` before the migration are held by the bridge contract. After migration, `sign_transfer` panics for every such pending transfer. Because there is no cancel or refund entrypoint, those tokens are permanently unrecoverable. The `locked_tokens` accounting divergence additionally means that future `fin_transfer` calls for the new token will silently skip the unlock step, leaving the bridge's internal accounting permanently inconsistent.

### Likelihood Explanation
Token migrations are an expected operational event (the contract already has `migrate_deployed_token` and `migrated_tokens` infrastructure). Any window between a user's `ft_transfer_call` and the DAO's `migrate_deployed_token` call is sufficient to trigger the lock. Because NEAR transactions are asynchronous and migrations are not preceded by a mandatory drain of `pending_transfers`, this window is realistic in production.

### Recommendation
Before executing the address re-keying, `migrate_deployed_token` should:
1. Require that `locked_tokens[(origin_chain, old_token)] == 0` (no outstanding locked balance), or atomically migrate the locked balance to the new key.
2. Either require `pending_transfers` to be empty for `old_token`, or iterate and rewrite each pending entry to reference `new_token` (updating the stored `TransferMessage.token` field).
3. Alternatively, make `get_token_id` consult `migrated_tokens` as a fallback so that `OmniAddress::Near(old_token)` transparently resolves to `new_token` during `sign_transfer`.

### Proof of Concept

1. User calls `old_token.ft_transfer_call(bridge, amount, msg=InitTransfer{recipient: eth_address})`. Bridge stores `pending_transfers[{Near, nonce}] = TransferMessage { token: OmniAddress::Near(old_token), ... }` and holds `amount` of `old_token`.
2. DAO calls `migrate_deployed_token(Eth, old_token, new_token)`. `token_id_to_address[(Eth, old_token)]` is deleted; `token_id_to_address[(Eth, new_token)]` is inserted.
3. Relayer calls `sign_transfer({Near, nonce}, ...)`. Inside, `get_token_id(OmniAddress::Near(old_token))` returns `old_token`. Then `get_token_address(Eth, old_token)` returns `None` → `env::panic_str("ERR_FAILED_TO_GET_TOKEN_ADDRESS")`.
4. `sign_transfer` is permanently broken for this transfer ID. The user's `amount` of `old_token` (now held by the bridge) is unrecoverable. [5](#0-4) [3](#0-2) [4](#0-3) [6](#0-5)

### Citations

**File:** near/omni-bridge/src/lib.rs (L466-473)
```rust
        let token_address = self
            .get_token_address(
                transfer_message.get_destination_chain(),
                self.get_token_id(&transfer_message.token),
            )
            .unwrap_or_else(|| {
                env::panic_str(BridgeError::FailedToGetTokenAddress.to_string().as_str())
            });
```

**File:** near/omni-bridge/src/lib.rs (L544-557)
```rust
        let transfer_message = TransferMessage {
            origin_nonce: self.current_origin_nonce,
            token: OmniAddress::Near(token_id),
            amount,
            recipient: init_transfer_msg.recipient,
            fee: Fee {
                fee: init_transfer_msg.fee,
                native_fee: init_transfer_msg.native_token_fee,
            },
            sender: OmniAddress::Near(sender_id),
            msg: init_transfer_msg.msg.map(String::from).unwrap_or_default(),
            destination_nonce,
            origin_transfer_id: None,
        };
```

**File:** near/omni-bridge/src/lib.rs (L1372-1380)
```rust
    pub fn get_token_id(&self, address: &OmniAddress) -> AccountId {
        if let OmniAddress::Near(token_account_id) = address {
            token_account_id.clone()
        } else {
            self.token_address_to_id
                .get(address)
                .near_expect(BridgeError::TokenNotRegistered)
        }
    }
```

**File:** near/omni-bridge/src/lib.rs (L1609-1669)
```rust
    #[access_control_any(roles(Role::DAO))]
    #[payable]
    pub fn migrate_deployed_token(
        &mut self,
        origin_chain: ChainKind,
        old_token: AccountId,
        new_token: AccountId,
    ) {
        require!(
            env::attached_deposit() >= NEP141_DEPOSIT,
            BridgeError::NotEnoughAttachedDeposit.as_ref()
        );

        require!(
            self.deployed_tokens.remove(&old_token),
            BridgeError::OldTokenNotDeployed.as_ref(),
        );
        require!(
            self.deployed_tokens.insert(&new_token),
            BridgeError::TokenExists.as_ref()
        );
        self.deployed_tokens_v2.remove(&old_token);
        self.deployed_tokens_v2.insert(&new_token, &origin_chain);

        let origin_address = self
            .token_id_to_address
            .remove(&(origin_chain, old_token.clone()))
            .near_expect(BridgeError::FailedToGetTokenAddress);

        require!(
            self.token_id_to_address
                .insert(&(origin_chain, new_token.clone()), &origin_address)
                .is_none(),
            BridgeError::TokenExists.as_ref()
        );

        self.token_address_to_id
            .insert(&origin_address, &new_token)
            .near_expect(BridgeError::ExpectedToOverwriteTokenAddress);

        require!(
            self.migrated_tokens
                .insert(&old_token, &new_token)
                .is_none(),
            BridgeError::TokenAlreadyMigrated.as_ref()
        );

        ext_token::ext(new_token.clone())
            .with_static_gas(STORAGE_DEPOSIT_GAS)
            .with_attached_deposit(NEP141_DEPOSIT)
            .storage_deposit(&env::current_account_id(), Some(true))
            .detach();

        env::log_str(
            &OmniBridgeEvent::MigrateTokenEvent {
                old_token_id: old_token,
                new_token_id: new_token,
            }
            .to_log_string(),
        );
    }
```

**File:** near/omni-bridge/src/token_lock.rs (L54-57)
```rust
        let key = (chain_kind, token_id.clone());
        let Some(current_amount) = self.locked_tokens.get(&key) else {
            return LockAction::Unchanged;
        };
```
