### Title
Replayable off-chain approval in `transfer_from` allows unlimited draining of a signer's stablecoin balance - (File: `aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move`)

### Summary
The `usdk` managed-stablecoin example implements an ERC20-style `approve`/`transferFrom` pattern using an off-chain signed `Approval` message instead of allowances. The "nonce" bound into the signed message is `account::get_sequence_number(from)` [1](#0-0) . This sequence number only advances when the **owner** (`from`) submits their own transactions — it is never touched by the spender calling `transfer_from`. Because `account::verify_signed_message` only checks the signature against the current authentication key and performs no allowance/nonce bookkeeping [2](#0-1) , a single signed `Approval` can be replayed by the same spender any number of times in separate transactions, each moving `amount` out of `from`'s primary store, until `from` happens to submit an unrelated transaction of their own. This is the Move-native analog of the ERC20 "approve race"/non-reset issue: instead of a stale allowance being reusable, here a supposedly one-time signed approval is fully reusable, with no cap on cumulative amount transferred.

### Finding Description
`transfer_from` in `usdk.move` is meant to let a `spender` move `amount` tokens out of `from`'s account, authorized by `from`'s off-chain signature over an `Approval` message:

```
public fun transfer_from(
    spender: &signer,
    proof: vector<u8>,
    from: address,
    from_account_scheme: u8,
    from_public_key: vector<u8>,
    to: address,
    amount: u64,
) acquires Management, State {
    ...
    let expected_message = Approval {
        owner: from,
        to: to,
        nonce: account::get_sequence_number(from),
        chain_id: chain_id::get(),
        spender: signer::address_of(spender),
        amount,
    };
    account::verify_signed_message(from, from_account_scheme, from_public_key, proof, expected_message);

    let transfer_ref = &borrow_global<Management>(usdk_address()).transfer_ref;
    primary_fungible_store::transfer_with_ref(transfer_ref, from, to, amount);
}
``` [3](#0-2) 

The intended replay-protection field is `nonce: account::get_sequence_number(from)`. `get_sequence_number` reads `Account.sequence_number` for the owner address [4](#0-3) . That counter is only incremented as part of Aptos transaction prologue/epilogue processing for transactions **sent by** the `from` account itself — `transfer_from` is submitted by `spender`, not `from`, and nowhere in this call path is `from`'s sequence number bumped or any consumed-nonce/allowance state recorded. `account::verify_signed_message` itself only checks the ed25519/multi-ed25519 signature against the account's current auth key; it has no side effect that invalidates the message after use [2](#0-1) .

Consequently:
- The exact same `(proof, from, from_account_scheme, from_public_key, to, amount)` tuple continues to produce a message whose `nonce` field is unchanged and whose signature remains valid for as long as `from` does not submit any transaction of its own.
- `spender` (the party who received the one-time approval) can call `transfer_from` repeatedly, each call moving another `amount` from `from`'s primary fungible store to `to`, until `from`'s balance is exhausted or `from` happens to transact (an event entirely outside `from`'s control/awareness as an "approval reset").
- Unlike a standard ERC20 allowance (which decrements per use and is capped at the approved value), this scheme has **no cap at all** on cumulative transferred amount — it is strictly worse than the "did not approve to zero first" class of bug, since here the approval is not even single-use.

The corrupted state is the `FungibleStore.balance` of `from`'s primary store: repeated `transfer_with_ref` calls move `amount` units out of custody each time the message is replayed, with no on-chain tracking that the authorization was already consumed [5](#0-4) .

### Impact Explanation
This breaks the custody invariant that an off-chain-signed, amount-bounded transfer authorization can only move the approved value once. A malicious or compromised `spender` who has ever received a legitimately signed `Approval` (e.g., for a single dApp checkout) can replay it to drain the owner's entire USDK balance, moving value to an address of the spender's choosing (`to`, which is fixed in the signed message, but the spender can still repeat the drain to that same destination they control or collude with). This is a direct theft-of-asset / custody-corruption impact on a live fungible asset (a stablecoin) with no privileged assumption required beyond holding one valid signed approval — it is a High/Critical severity issue for any deployment of this pattern.

### Likelihood Explanation
Likelihood is high wherever this `transfer_from` pattern is used as designed (e.g., a dApp requests one signed approval for a single payment). The replay does not require any race condition, front-running, or special timing — it works reliably as long as the owner's account doesn't submit an unrelated transaction, which is common for many wallets/dApp flows (an EOA may go long periods without initiating any transaction itself, especially in custody/embedded-wallet setups where users only ever sign off-chain approvals).

### Recommendation
- Do not rely on `account::get_sequence_number` as a "nonce" for permit-style approvals, since it is controlled by the owner submitting transactions, not by any consumption in this flow.
- Introduce an explicit, monotonically-increasing (or single-use) nonce/allowance resource stored under the `usdk` module (e.g., a `Table<address, u64>` of used nonces per owner, or a per-owner allowance mapping decremented on each use) and require the caller to supply/increment it as part of `transfer_from`, then assert it hasn't been used before.
- Alternatively, bind the approval to a strict single-use marker (hash of the full `Approval` struct) that is recorded on first use and checked/rejected on subsequent calls.
- Follow the ERC-2612/EIP-712 permit pattern's approach of a dedicated per-owner incrementing nonce state that only the permit-consuming function itself advances.

### Proof of Concept
1. Owner `from` signs one `Approval { owner: from, to: to, nonce: account::get_sequence_number(from), chain_id, spender, amount }` message and hands the `proof` bytes to `spender` for a single intended payment of `amount`.
2. `spender` calls `usdk::transfer_from(spender, proof, from, scheme, pubkey, to, amount)`. This succeeds: `verify_signed_message` validates the signature, and `amount` is moved from `from`'s primary store to `to`'s primary store via `primary_fungible_store::transfer_with_ref` [6](#0-5) .
3. `spender` calls `usdk::transfer_from` again with the exact same arguments (`proof`, `from`, `amount`, etc.). Because `from` has not submitted any transaction of its own, `account::get_sequence_number(from)` is unchanged, so the `expected_message` reconstructed inside `transfer_from` is bit-for-bit identical to the one originally signed, and `verify_signed_message` succeeds again.
4. Step 3 can be repeated indefinitely (bounded only by `from`'s remaining balance), draining the account well beyond the single `amount` the owner intended to authorize.

### Citations

**File:** aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move (L162-188)
```text
    public fun transfer_from(
        spender: &signer,
        proof: vector<u8>,
        from: address,
        from_account_scheme: u8,
        from_public_key: vector<u8>,
        to: address,
        amount: u64,
    ) acquires Management, State {
        assert_not_paused();
        assert_not_denylisted(from);
        assert_not_denylisted(to);

        let expected_message = Approval {
            owner: from,
            to: to,
            nonce: account::get_sequence_number(from),
            chain_id: chain_id::get(),
            spender: signer::address_of(spender),
            amount,
        };
        account::verify_signed_message(from, from_account_scheme, from_public_key, proof, expected_message);

        let transfer_ref = &borrow_global<Management>(usdk_address()).transfer_ref;
        // Only use with_ref API for primary_fungible_store (PFS) transfers in this module.
        primary_fungible_store::transfer_with_ref(transfer_ref, from, to, amount);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/account/account.move (L1261-1267)
```text
    ): SignerCapabilityOfferProofChallengeV2 acquires Account {
        SignerCapabilityOfferProofChallengeV2 {
            sequence_number: get_sequence_number(source_address),
            source_address,
            recipient_address,
        }
    }
```

**File:** aptos-move/framework/aptos-framework/sources/account/account.move (L1282-1320)
```text
    public fun verify_signed_message<T: drop>(
        account: address,
        account_scheme: u8,
        account_public_key: vector<u8>,
        signed_message_bytes: vector<u8>,
        message: T,
    ) acquires Account {
        let auth_key = get_authentication_key(account);
        // Verify that the `SignerCapabilityOfferProofChallengeV2` has the right information and is signed by the account owner's key
        if (account_scheme == ED25519_SCHEME) {
            let pubkey = ed25519::new_unvalidated_public_key_from_bytes(account_public_key);
            let expected_auth_key = ed25519::unvalidated_public_key_to_authentication_key(&pubkey);
            assert!(
                auth_key == expected_auth_key,
                error::invalid_argument(EWRONG_CURRENT_PUBLIC_KEY),
            );

            let signer_capability_sig = ed25519::new_signature_from_bytes(signed_message_bytes);
            assert!(
                ed25519::signature_verify_strict_t(&signer_capability_sig, &pubkey, message),
                error::invalid_argument(EINVALID_PROOF_OF_KNOWLEDGE),
            );
        } else if (account_scheme == MULTI_ED25519_SCHEME) {
            let pubkey = multi_ed25519::new_unvalidated_public_key_from_bytes(account_public_key);
            let expected_auth_key = multi_ed25519::unvalidated_public_key_to_authentication_key(&pubkey);
            assert!(
                auth_key == expected_auth_key,
                error::invalid_argument(EWRONG_CURRENT_PUBLIC_KEY),
            );

            let signer_capability_sig = multi_ed25519::new_signature_from_bytes(signed_message_bytes);
            assert!(
                multi_ed25519::signature_verify_strict_t(&signer_capability_sig, &pubkey, message),
                error::invalid_argument(EINVALID_PROOF_OF_KNOWLEDGE),
            );
        } else {
            abort error::invalid_argument(EINVALID_SCHEME)
        };
    }
```

**File:** aptos-move/framework/aptos-framework/sources/primary_fungible_store.move (L270-280)
```text
    /// Transfer `amount` of FA from the primary store of `from` to that of `to` ignoring frozen flag.
    public fun transfer_with_ref(
        transfer_ref: &TransferRef,
        from: address,
        to: address,
        amount: u64
    ) acquires DeriveRefPod {
        let from_primary_store = primary_store(from, transfer_ref.transfer_ref_metadata());
        let to_primary_store = ensure_primary_store_exists(to, transfer_ref.transfer_ref_metadata());
        transfer_ref.transfer_with_ref(from_primary_store, to_primary_store, amount);
    }
```
