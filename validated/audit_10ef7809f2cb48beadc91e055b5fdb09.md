### Title
Access Key Nonce Reset on Same-Block Delete+Re-Add Enables Transaction Replay - (File: runtime/runtime/src/access_keys.rs)

### Summary
When an access key is deleted and re-added with the same public key within the same block, the nonce is reset to `(block_height - 1) * ACCESS_KEY_NONCE_RANGE_MULTIPLIER` rather than being preserved. This violates the documented invariant and allows an unprivileged observer to replay any previously-processed transaction signed with that key whose nonce falls above the reset value, within the transaction validity window.

### Finding Description

`add_regular_key` unconditionally overwrites the nonce with `initial_nonce_value(block_height)`: [1](#0-0) [2](#0-1) 

`initial_nonce_value(block_height)` returns `(block_height - 1) * MULTIPLIER`. It does **not** read or preserve the nonce that was stored on the key before deletion.

The `AccessKey` data-structure documentation explicitly states the invariant that is broken: [3](#0-2) 

`action_delete_key` simply removes the key from the trie with no nonce bookkeeping: [4](#0-3) 

A single transaction whose action list is `[DeleteKey(K), AddKey(K)]` is therefore sufficient to reset the nonce. The existing test suite even acknowledges the gap: [5](#0-4) 

### Impact Explanation

**Corrupted protocol value**: the `access_key.nonce` stored in the account trie is set to a value lower than nonces already consumed in the same block. Any `SignedTransaction` whose `tx_nonce` satisfies

```
(block_height - 1) * MULTIPLIER  <  tx_nonce  <  block_height * MULTIPLIER
```

and whose `block_hash` is still within the `transaction_validity_period` window passes the monotonic nonce check: [6](#0-5) 

A replayed transfer drains the signer's balance a second time; a replayed `AddKey` / `DeleteKey` / `FunctionCall` can have equivalent second-order effects. The corrupted value is the on-chain `AccessKey.nonce` entry in the state trie, leading to a corrupted account balance.

### Likelihood Explanation

**Trigger condition**: T1 (a transfer or other action signed with key K) and T2 (`[DeleteKey(K), AddKey(K)]`) must land in the **same block**, with T1 ordered before T2 in chunk processing. This is a narrow but realistic window:

- A user who wants to change a key's permission (e.g., FunctionCall → FullAccess) issues `[DeleteKey(K), AddKey(K, FullAccess)]` as a single transaction. If they also submitted a transfer with the same key in the same block (e.g., two back-to-back RPC calls), the nonce resets below the transfer's nonce.
- An attacker who monitors the public mempool/chain can detect the reset and immediately resubmit the original signed transaction before the `block_hash` validity period expires (~100 blocks / ~100 seconds on mainnet).

No special privileges are required: the attacker only needs to observe public chain data and submit a standard RPC transaction.

### Recommendation

In `add_regular_key`, read the existing key's nonce before deletion and use `max(initial_nonce_value(block_height), old_nonce)` when writing the new key, matching the documented invariant. Alternatively, enforce that `AddKey` for a public key that was deleted in the same transaction batch is rejected, or that `DeleteKey` + `AddKey` in the same action list is treated as a key-update that preserves the nonce.

### Proof of Concept

1. At block H, victim submits two transactions in quick succession (same chunk):
   - **T1**: `Transfer(100 NEAR → attacker)`, signed with key K, nonce = `(H-1)*M + 5`
   - **T2**: `[DeleteKey(K), AddKey(K, FullAccess)]`, signed with key K, nonce = `(H-1)*M + 6`

2. Chunk processing order: T1 first, T2 second.
   - After T1: `access_key[K].nonce = (H-1)*M + 5`; transfer receipt queued.
   - After T2 receipt: `access_key[K].nonce = (H-1)*M` (reset by `add_regular_key`).

3. Attacker resubmits T1 (identical bytes, same signature) in block H+1 with a fresh `block_hash` pointing to block H. The nonce check passes: `(H-1)*M + 5 > (H-1)*M`. The transfer executes a second time.

4. Victim loses 200 NEAR total instead of 100 NEAR. [1](#0-0) [7](#0-6) [8](#0-7)

### Citations

**File:** runtime/runtime/src/access_keys.rs (L46-50)
```rust
pub(crate) fn initial_nonce_value(block_height: BlockHeight) -> Nonce {
    // Set default nonce for newly created access key to avoid transaction hash collision.
    // See <https://github.com/near/nearcore/issues/3779>.
    (block_height - 1) * near_primitives::account::AccessKey::ACCESS_KEY_NONCE_RANGE_MULTIPLIER
}
```

**File:** runtime/runtime/src/access_keys.rs (L52-91)
```rust
pub(crate) fn action_delete_key(
    config: &RuntimeConfig,
    state_update: &mut TrieUpdate,
    account: &mut Account,
    result: &mut ActionResult,
    account_id: &AccountId,
    delete_key: &DeleteKeyAction,
) -> Result<(), RuntimeError> {
    let access_key = get_access_key(state_update, account_id, &delete_key.public_key)?;
    if let Some(access_key) = access_key {
        if let Some(gas_key_info) = access_key.gas_key_info() {
            delete_gas_key(
                config,
                state_update,
                account,
                result,
                account_id,
                &delete_key.public_key,
                &access_key,
                gas_key_info,
            )?;
        } else {
            delete_regular_key(
                &config.fees,
                state_update,
                account,
                account_id,
                &delete_key.public_key,
                &access_key,
            );
        }
    } else {
        result.result = Err(ActionErrorKind::DeleteKeyDoesNotExist {
            public_key: delete_key.public_key.clone().into(),
            account_id: account_id.clone(),
        }
        .into());
    }
    Ok(())
}
```

**File:** runtime/runtime/src/access_keys.rs (L136-147)
```rust
fn delete_regular_key(
    fee_config: &RuntimeFeesConfig,
    state_update: &mut TrieUpdate,
    account: &mut Account,
    account_id: &AccountId,
    public_key: &PublicKey,
    access_key: &AccessKey,
) {
    let storage_usage = access_key_storage_usage(fee_config, public_key, access_key);
    remove_access_key(state_update, account_id.clone(), public_key.clone());
    account.set_storage_usage(account.storage_usage().saturating_sub(storage_usage));
}
```

**File:** runtime/runtime/src/access_keys.rs (L230-255)
```rust
fn add_regular_key(
    fee_config: &RuntimeFeesConfig,
    state_update: &mut TrieUpdate,
    account: &mut Account,
    account_id: &AccountId,
    public_key: &PublicKey,
    access_key: &AccessKey,
    block_height: BlockHeight,
) -> Result<(), StorageError> {
    let mut access_key = access_key.clone();
    access_key.nonce = initial_nonce_value(block_height);
    set_access_key(state_update, account_id.clone(), public_key.clone(), &access_key);

    account.set_storage_usage(
        account
            .storage_usage()
            .checked_add(access_key_storage_usage(fee_config, public_key, &access_key))
            .ok_or_else(|| {
                StorageError::StorageInconsistentState(format!(
                    "Storage usage integer overflow for account {}",
                    account_id
                ))
            })?,
    );
    Ok(())
}
```

**File:** docs/DataStructures/AccessKey.md (L8-12)
```markdown
    /// The nonce for this access key.
    /// NOTE: In some cases the access key needs to be recreated. If the new access key reuses the
    /// same public key, the nonce of the new access key should be equal to the nonce of the old
    /// access key. It's required to avoid replaying old transactions again.
    pub nonce: Nonce,
```

**File:** integration-tests/src/tests/standard_cases/mod.rs (L1112-1116)
```rust
            // TODO(#6724): This is a wrong error, the transaction actually
            // succeeds. We get an error here when we retry the tx and the second
            // time around it fails. Normally, retries are handled by nonces, but we
            // forget the nonce when we delete a key!
            assert_eq!(
```

**File:** runtime/runtime/src/verifier.rs (L217-236)
```rust
    match nonce_mode {
        NonceMode::Monotonic => {
            if tx_nonce <= current_nonce {
                return Err(InvalidTxError::InvalidNonce { tx_nonce, ak_nonce: current_nonce });
            }
        }
        NonceMode::Strict => {
            if !current_nonce.checked_add(1).is_some_and(|expected| tx_nonce == expected) {
                return Err(InvalidTxError::InvalidNonce { tx_nonce, ak_nonce: current_nonce });
            }
        }
    }
    if let Some(height) = block_height {
        let upper_bound = height
            .saturating_mul(near_primitives::account::AccessKey::ACCESS_KEY_NONCE_RANGE_MULTIPLIER);
        if tx_nonce >= upper_bound {
            return Err(InvalidTxError::NonceTooLarge { tx_nonce, upper_bound });
        }
    }
    Ok(())
```
