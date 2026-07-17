### Title
Gas Check Uses `prepaid_gas()` Instead of `prepaid_gas() - used_gas()` Allows Nonce Consumption Without Action Execution — (File: `runtime/near-wallet-contract/implementation/wallet-contract/src/internal.rs`)

---

### Summary

The `WalletContract`'s gas adequacy check in `validate_tx_relayer_data` uses `env::prepaid_gas()` (total gas attached to the call) rather than `env::prepaid_gas() - env::used_gas()` (gas remaining after execution so far). This is the same root-cause class as the reported token-bridge bug. A malicious relayer can inflate gas consumption in the first receipt via oversized JSON arguments with ignored fields, causing the nonce to be permanently incremented while the intended action promise fails — an exact structural analog of the VAA-marked-used-without-transfer pattern.

---

### Finding Description

`WalletContract` stores two critical state fields:

```rust
pub struct WalletContract {
    pub nonce: u64,
    pub has_in_flight_tx: bool,
}
``` [1](#0-0) 

The entry point `rlp_execute` calls `inner_rlp_execute`, which calls `internal::parse_rlp_tx_to_action`, which calls `validate_tx_relayer_data`. The gas check there is:

```rust
if env::prepaid_gas().as_gas() < gas_limit.saturating_mul(GAS_MULTIPLIER) {
    return Err(Error::Relayer(RelayerError::InsufficientGas));
}
``` [2](#0-1) 

This check uses `env::prepaid_gas()` — the **total** gas attached to the call — not `env::prepaid_gas() - env::used_gas()` (gas **remaining** after JSON parsing and prior execution). The NEAR SDK deserializes function arguments from JSON before the contract body runs. Any extra JSON fields that do not match parameter names are silently ignored by the SDK, but their parsing still consumes gas. A relayer who submits a call with a large blob of ignored JSON fields can exhaust most of the gas budget before `validate_tx_relayer_data` is even reached, yet the check still passes because it reads the original prepaid total.

After the check passes, the nonce is incremented unconditionally (for non-registrar paths):

```rust
*nonce = nonce.saturating_add(1);
``` [3](#0-2) 

Then the action promise is created and the receipt completes. The nonce increment is committed to state. The subsequent action receipt (the actual transfer, function call, etc.) then fails because the gas budget was exhausted by the inflated JSON parsing in the first receipt. The callback `rlp_execute_callback` is still invoked (it has `RLP_EXECUTE_CALLBACK_GAS = 5 TGas` reserved statically), resets `has_in_flight_tx = false`, but the nonce is already permanently incremented. [4](#0-3) 

The structural parallel to the token-bridge bug is exact:

| Token-bridge | Wallet Contract |
|---|---|
| `self.dups.insert(&pvaa.hash, &true)` before promise | `*nonce = nonce.saturating_add(1)` before promise |
| Gas check uses `prepaid_gas()` | Gas check uses `prepaid_gas()` |
| VAA marked used, transfer fails | Nonce consumed, action fails |
| User cannot receive tokens | User's signed tx permanently invalidated |

---

### Impact Explanation

The corrupted protocol value is `WalletContract::nonce` stored in the NEAR trie. After the attack, the nonce is `N+1` but the user's intended action (e.g., a NEAR token transfer or function call encoded in the Ethereum transaction) was never executed. The user's signed Ethereum transaction with nonce `N` is permanently invalidated — it cannot be replayed because the nonce has advanced. The user must re-sign a new transaction with nonce `N+1`. A persistent attacker can repeat this for every new transaction the user submits, effectively denying the user the ability to execute any action through the wallet contract.

---

### Likelihood Explanation

`rlp_execute` is `#[payable]` and callable by any account — no special privilege is required to be a relayer. The attacker controls the JSON arguments they submit. The binary-search technique described in the original report (finding the exact JSON size that lets the first receipt succeed while starving the second) applies directly here. The attack is cheap for the attacker (they spend gas) and repeatable.

---

### Recommendation

Replace the gas check with the remaining-gas form:

```rust
// Before (vulnerable):
if env::prepaid_gas().as_gas() < gas_limit.saturating_mul(GAS_MULTIPLIER) { ... }

// After (fixed):
let remaining = env::prepaid_gas().as_gas().saturating_sub(env::used_gas().as_gas());
if remaining < gas_limit.saturating_mul(GAS_MULTIPLIER) { ... }
```

This mirrors the fix applied to the token-bridge contract (commit `4589e89` in the original report), which changed the check from `env::prepaid_gas()` to `env::prepaid_gas() - env::used_gas()`.

---

### Proof of Concept

1. User signs an Ethereum transaction with nonce `N` encoding a NEAR action (e.g., a token transfer).
2. Attacker (any account acting as relayer) calls `rlp_execute(target, tx_bytes_b64)` with the user's valid signed bytes, but pads the JSON call arguments with a large blob of ignored fields:
   ```json
   { "ignored_field": "AAAA...AAAA (megabytes)", "target": "...", "tx_bytes_b64": "..." }
   ```
3. The NEAR SDK JSON parser processes all fields (including ignored ones), consuming most of the gas budget before the contract body runs.
4. `validate_tx_relayer_data` checks `env::prepaid_gas()` — the original total — which still passes.
5. `inner_rlp_execute` increments `self.nonce` to `N+1` and creates the action promise.
6. The `rlp_execute` receipt completes successfully; the nonce increment is committed to trie state.
7. The action receipt (the actual transfer) fails with `GasExceeded` because the gas budget was exhausted.
8. `rlp_execute_callback` executes (5 TGas reserved), sets `has_in_flight_tx = false`, reports failure.
9. The user's transaction with nonce `N` is permanently invalidated; the intended action never executed. [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L37-37)
```rust
const RLP_EXECUTE_CALLBACK_GAS: Gas = Gas::from_tgas(5);
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L46-55)
```rust
pub struct WalletContract {
    pub nonce: u64,
    /// Tracks whether a transaction is currently being executed
    /// (i.e. has receipts that have not yet resolved).
    /// Invariant: `has_in_flight_tx` must be `true` when a mutable method
    /// of this contract returns a promise and `false` otherwise (except
    /// for the check if a transaction is already in flight at the beginning
    /// of `rlp_execute`).
    pub has_in_flight_tx: bool,
}
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L108-128)
```rust
        let result = inner_rlp_execute(
            current_account_id.clone(),
            predecessor_account_id,
            target,
            tx_bytes_b64,
            &mut self.nonce,
        );

        match result {
            Ok(promise) => {
                self.has_in_flight_tx = true;
                PromiseOrValue::Promise(promise)
            }
            Err(Error::Relayer(_)) if env::signer_account_id() == current_account_id => {
                let promise = create_ban_relayer_promise(current_account_id);
                self.has_in_flight_tx = true;
                PromiseOrValue::Promise(promise)
            }
            Err(e) => PromiseOrValue::Value(e.into()),
        }
    }
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/lib.rs (L330-410)
```rust
fn inner_rlp_execute(
    current_account_id: AccountId,
    predecessor_account_id: AccountId,
    target: AccountId,
    tx_bytes_b64: String,
    nonce: &mut u64,
) -> Result<Promise, Error> {
    if *nonce == u64::MAX {
        return Err(Error::AccountNonceExhausted);
    }
    let context = ExecutionContext::new(
        current_account_id.clone(),
        predecessor_account_id,
        env::attached_deposit(),
    )?;
    let caller_deposit = CallerDeposit::new(&context);

    let parsing_result = internal::parse_rlp_tx_to_action(&tx_bytes_b64, &target, &context, *nonce);
    let (action, transaction_kind) = match parsing_result {
        Ok((action, transaction_kind)) => {
            // Increment nonce for all cases where the registrar contract is not needed
            // to prevent replay of those transactions. For transactions that go through
            // the registrar we still do not know if the transaction has a relayer error
            // or not, therefore we must delay incrementing the nonce.
            //
            // Note: relayers with access keys cannot use this delay to needlessly spend
            // the users tokens because only one transaction is allowed to be in-flight
            // at a time.
            if let TransactionKind::EthEmulation(EthEmulationKind::EOABaseTokenTransfer {
                address_check: Some(_),
                ..
            }) = &transaction_kind
            {
            } else {
                *nonce = nonce.saturating_add(1);
            }

            // If the action is an emulated base token or ERC-20 transfer with a non-zero fee then
            // create a promise to send the refund to the relayer. This allows any relayer
            // to safely serve base token transfers from any wallet without additional
            // on-boarding because the relayer will receive some compensation for sending
            // the transaction. Users should always verify the fee before signing a base token
            // transfer. Relayers should also verify the fee before sending to make sure the
            // user's signed transaction will refund enough to cover the relayer's gas costs.
            if let TransactionKind::EthEmulation(EthEmulationKind::EOABaseTokenTransfer {
                fee,
                ..
            })
            | TransactionKind::EthEmulation(EthEmulationKind::ERC20Transfer { fee, .. }) =
                &transaction_kind
            {
                if !fee.is_zero() && context.predecessor_account_id != context.current_account_id {
                    let refund_promise = env::promise_batch_create(&context.predecessor_account_id);
                    env::promise_batch_action_transfer(refund_promise, *fee);
                }
            }

            (action, transaction_kind)
        }
        Err(err @ Error::User(_)) => {
            // Increment nonce on all user errors to prevent replay.
            *nonce = nonce.saturating_add(1);
            return Err(err);
        }
        Err(err) => {
            // Do not increment nonce on Relayer or AccountId errors.
            // The latter error is an issue in the deployment (so the nonce is meaningless).
            // The former arises from the relayer itself doing something wrong and thus the
            // user's transaction could still be valid and potentially submitted properly by
            // another relayer. To allow this we do not increment the nonce.
            //
            // Note: if a relayer is using an access key for this wallet then that key will
            // still be revoked (in the main logic of `rlp_execute`). This fact together with
            // the condition that there only be one in-flight transaction at a time implies
            // that a relayer cannot maliciously burn a large portion of the user's tokens.
            // If the relayer is not using an access key then they are spending their own
            // resources on the gas and therefore we do not care if the relayer submits
            // the same faulty transaction multiple times.
            return Err(err);
        }
    };
```

**File:** runtime/near-wallet-contract/implementation/wallet-contract/src/internal.rs (L312-368)
```rust
/// Validates the transaction is following the Wallet Contract protocol.
/// This includes checks for:
/// - from address matches current account address
/// - to address is present and matches the target address (or hash of target account ID)
/// - nonce matches expected nonce
/// If this validation fails then the relayer that sent it is faulty and should be banned.
fn validate_tx_relayer_data<'a>(
    tx: &NormalizedEthTransaction,
    target: &'a AccountId,
    context: &ExecutionContext,
    expected_nonce: u64,
) -> Result<TargetKind<'a>, Error> {
    if tx.address.raw() != context.current_address {
        return Err(Error::Relayer(RelayerError::InvalidSender));
    }

    if tx.chain_id != Some(CHAIN_ID) {
        return Err(Error::Relayer(RelayerError::InvalidChainId));
    }

    let to = tx.to.ok_or(Error::User(UserError::EvmDeployDisallowed))?.raw();

    let target_kind = parse_target(target, context.current_address);

    // valid targets satisfy `to == target` or `to == hash(target)`
    let is_valid_target = match target_kind {
        TargetKind::CurrentAccount if to == context.current_address => {
            target == &context.current_account_id
        }
        TargetKind::EthImplicit(address) if to == address => {
            target.as_str()
                == format!("0x{}{}", hex::encode(address), context.current_account_suffix())
        }
        _ => to == account_id_to_address(target),
    };

    if !is_valid_target {
        return Err(Error::Relayer(RelayerError::InvalidTarget));
    }

    let nonce = if tx.nonce <= U64_MAX {
        tx.nonce.low_u64()
    } else {
        return Err(Error::Relayer(RelayerError::InvalidNonce));
    };
    if nonce != expected_nonce {
        return Err(Error::Relayer(RelayerError::InvalidNonce));
    }

    // Relayers must attach at least as much gas as the user requested.
    let gas_limit = if tx.gas_limit < U64_MAX { tx.gas_limit.as_u64() } else { u64::MAX };
    if env::prepaid_gas().as_gas() < gas_limit.saturating_mul(GAS_MULTIPLIER) {
        return Err(Error::Relayer(RelayerError::InsufficientGas));
    }

    Ok(target_kind)
}
```
