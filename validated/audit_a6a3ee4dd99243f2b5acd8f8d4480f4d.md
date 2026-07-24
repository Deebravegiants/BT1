### Title
`init_transfer` accepts transfers to unconfigured destination chains, permanently locking user tokens - (File: `near/omni-bridge/src/lib.rs`)

### Summary

The NEAR bridge's `init_transfer` function only validates that the destination chain is not `Near`, but does not verify that the destination chain has a registered factory or that the token is registered for that chain. A user can initiate a transfer to any `ChainKind` variant (e.g., `Aptos`, `Fogo`) that exists in the enum but has no token mapping configured. The tokens are consumed by the bridge and stored in `pending_transfers`, but `sign_transfer` will always panic because `get_token_address` returns `None` for the unconfigured chain. No cancel or refund path exists, making the lock permanent.

### Finding Description

`ft_on_transfer` dispatches to `init_transfer` for any `InitTransfer` message. The only destination-chain guard is:

```rust
require!(
    init_transfer_msg.recipient.get_chain() != ChainKind::Near,
    BridgeError::InvalidRecipientChain.as_ref()
);
``` [1](#0-0) 

No check is made against `self.factories` or `self.token_id_to_address`. Execution then reaches `init_transfer_internal`, which:

1. Stores the transfer in `pending_transfers` via `add_transfer_message`.
2. Calls `burn_tokens_if_needed` — burns the tokens if they are a deployed bridge token.
3. Calls `lock_tokens_if_needed` — silently returns `LockAction::Unchanged` if the `(chain_kind, token_id)` key is absent from `locked_tokens` (i.e., the token was never registered for that chain via `bind_token`).
4. Emits `InitTransferEvent` and returns `U128(0)` — signalling to the NEP-141 token contract that all tokens were consumed (no refund). [2](#0-1) 

The silent no-op in `lock_tokens` when the key is absent: [3](#0-2) 

Later, when a relayer calls `sign_transfer`, it calls `get_token_address(destination_chain, token_id)`, which returns `None` for any chain where the token was never registered, causing an unconditional panic:

```rust
let token_address = self
    .get_token_address(
        transfer_message.get_destination_chain(),
        self.get_token_id(&transfer_message.token),
    )
    .unwrap_or_else(|| {
        env::panic_str(BridgeError::FailedToGetTokenAddress.to_string().as_str())
    });
``` [4](#0-3) 

`get_token_address` is a simple map lookup with no fallback: [5](#0-4) 

There is no public `cancel_transfer` or admin sweep function. `remove_transfer_message` is private and only reachable through `sign_transfer_callback` or `claim_fee_callback`, both of which require a successful MPC signature or proof — impossible for an unconfigured chain.

### Impact Explanation

**Critical — Irreversible fund lock.**

- For native NEAR tokens (e.g., USDC.near): tokens are transferred to the bridge contract and held there permanently. `sign_transfer` always panics. No recovery path exists.
- For deployed bridge tokens (wrapped assets): tokens are burned by `burn_tokens_if_needed`. The corresponding mint on the destination chain never happens. Tokens are permanently destroyed.

The `locked_tokens` accounting is also silently skipped (returns `Unchanged`), so the bridge's internal supply tracking is inconsistent with actual holdings.

### Likelihood Explanation

**Medium.** The `ChainKind` enum already contains chains that may not be fully configured at any given time (`Aptos`, `Fogo`, `Abs`, `HyperEvm`, `Strk`). Any user who specifies a recipient on one of these chains before the corresponding token mapping is registered via `bind_token` will permanently lose their funds. The entry point is fully public (`ft_transfer_call` on any NEP-141 token), requires no special role, and the user-controlled `recipient` field in `InitTransferMsg` is the sole trigger. [6](#0-5) 

### Recommendation

Add a token-registration check inside `init_transfer` before consuming tokens:

```rust
fn init_transfer(
    &mut self,
    sender_id: AccountId,
    signer_id: AccountId,
    token_id: AccountId,
    amount: U128,
    init_transfer_msg: InitTransferMsg,
) -> PromiseOrPromiseIndexOrValue<U128> {
    require!(
        init_transfer_msg.recipient.get_chain() != ChainKind::Near,
        BridgeError::InvalidRecipientChain.as_ref()
    );
    // NEW: reject transfers to chains where the token has no registered address
    require!(
        self.get_token_address(
            init_transfer_msg.get_destination_chain(),
            token_id.clone()
        ).is_some(),
        BridgeError::TokenNotRegistered.as_ref()
    );
    // ... rest of function
}
```

Alternatively, validate that the destination chain has a registered factory:

```rust
require!(
    self.factories.get(&init_transfer_msg.get_destination_chain()).is_some(),
    BridgeError::UnknownFactory.as_ref()
);
```

The factory check is coarser (a chain can have a factory but no specific token registered), so the per-token check is preferred.

### Proof of Concept

1. Assume `Aptos` is in `ChainKind` but no token mapping exists for `(Aptos, usdc.near)` in `token_id_to_address`.
2. User calls `usdc.near::ft_transfer_call(bridge.near, 1_000_000, msg)` where `msg` is:
   ```json
   {"InitTransfer": {"recipient": "aptos:0x000...001", "fee": "0", "native_token_fee": "0"}}
   ```
3. Bridge's `ft_on_transfer` → `init_transfer` passes the only guard (`!= Near`).
4. `init_transfer_internal` stores the transfer, calls `burn_tokens_if_needed` (no-op for native token), calls `lock_tokens_if_needed` (silent no-op — no entry in `locked_tokens`), emits `InitTransferEvent`, returns `U128(0)`.
5. NEP-141 token contract receives `0` refund → 1,000,000 USDC transferred to bridge.
6. Any call to `sign_transfer` for this `TransferId` panics at `get_token_address` → `FailedToGetTokenAddress`.
7. No cancel function exists. 1,000,000 USDC is permanently locked in the bridge. [7](#0-6)

### Citations

**File:** near/omni-bridge/src/lib.rs (L256-287)
```rust
    #[pause(except(roles(Role::DAO, Role::UnrestrictedDeposit)))]
    pub fn ft_on_transfer(&mut self, sender_id: AccountId, amount: U128, msg: String) {
        let token_id = env::predecessor_account_id();
        let parsed_msg: BridgeOnTransferMsg = serde_json::from_str(&msg)
            .or_else(|_| serde_json::from_str(&msg).map(BridgeOnTransferMsg::InitTransfer))
            .near_expect(BridgeError::ParseMsg);

        // We can't trust sender_id to pay for storage as it can be spoofed.
        let signer_id = env::signer_account_id();
        let promise_or_promise_index_or_value = match parsed_msg {
            BridgeOnTransferMsg::InitTransfer(init_transfer_msg) => {
                self.init_transfer(sender_id, signer_id, token_id, amount, init_transfer_msg)
            }
            BridgeOnTransferMsg::FastFinTransfer(fast_fin_transfer_msg) => {
                self.fast_fin_transfer(token_id, amount, signer_id, fast_fin_transfer_msg)
            }
            BridgeOnTransferMsg::UtxoFinTransfer(utxo_fin_transfer_msg) => self.utxo_fin_transfer(
                token_id,
                amount,
                &signer_id,
                &sender_id,
                utxo_fin_transfer_msg,
            ),
            BridgeOnTransferMsg::SwapMigratedToken => {
                self.swap_migrated_token(sender_id, token_id, amount)
                    .detach();
                PromiseOrPromiseIndexOrValue::Value(U128(0))
            }
        };

        promise_or_promise_index_or_value.as_return();
    }
```

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

**File:** near/omni-bridge/src/lib.rs (L535-538)
```rust
        require!(
            init_transfer_msg.recipient.get_chain() != ChainKind::Near,
            BridgeError::InvalidRecipientChain.as_ref()
        );
```

**File:** near/omni-bridge/src/lib.rs (L1364-1370)
```rust
    pub fn get_token_address(
        &self,
        chain_kind: ChainKind,
        token: AccountId,
    ) -> Option<OmniAddress> {
        self.token_id_to_address.get(&(chain_kind, token))
    }
```

**File:** near/omni-bridge/src/lib.rs (L1834-1870)
```rust
    fn init_transfer_internal(
        &mut self,
        transfer_message: TransferMessage,
        storage_owner: AccountId,
    ) -> U128 {
        let required_storage_balance = self
            .add_transfer_message(transfer_message.clone(), storage_owner.clone())
            .saturating_add(NearToken::from_yoctonear(transfer_message.fee.native_fee.0));

        if self
            .try_update_storage_balance(
                storage_owner,
                required_storage_balance,
                NearToken::from_yoctonear(0),
            )
            .is_err()
        {
            self.remove_transfer_message_without_refund(transfer_message.get_transfer_id());
            return transfer_message.amount;
        }

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

        env::log_str(&OmniBridgeEvent::InitTransferEvent { transfer_message }.to_log_string());
        U128(0)
    }
```

**File:** near/omni-bridge/src/token_lock.rs (L48-57)
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
```

**File:** near/omni-types/src/lib.rs (L54-86)
```rust
pub enum ChainKind {
    #[default]
    #[serde(alias = "eth")]
    Eth,
    #[serde(alias = "near")]
    Near,
    #[serde(alias = "sol")]
    Sol,
    #[serde(alias = "arb")]
    Arb,
    #[serde(alias = "base")]
    Base,
    #[serde(alias = "bnb")]
    Bnb,
    #[serde(alias = "btc")]
    Btc,
    #[serde(alias = "zcash")]
    Zcash,
    #[serde(alias = "pol")]
    Pol,
    #[serde(rename = "HlEvm")]
    #[serde(alias = "hlevm")]
    #[strum(serialize = "HlEvm")]
    HyperEvm,
    #[serde(alias = "strk")]
    Strk,
    #[serde(alias = "abs")]
    Abs,
    #[serde(alias = "fogo")]
    Fogo,
    #[serde(alias = "aptos")]
    Aptos,
}
```
