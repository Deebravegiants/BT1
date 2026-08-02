### Title
`transfer_from` permit replay: unbounded custody drain via non-consuming nonce - ([File: aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move])

### Summary
The custody invariant reduced from the EIP-4494 report is: *a signature-based asset-authorization mechanism must bind each signed approval to a nonce that is verifiably consumed on first use, so the same signature cannot authorize more than one transfer.* `stablecoin::usdk::transfer_from` implements an EIP-2612/4494-style "permit" for fungible-asset custody but violates exactly this invariant: it uses the signer's live `sequence_number` as the "nonce" in the signed `Approval` message, yet never marks that nonce as used and never requires it to advance. Any party holding a validly signed `Approval` can replay it against `transfer_from` an unbounded number of times, draining `amount` from `from`'s primary store repeatedly until the balance is exhausted or `from` happens to submit an unrelated transaction (which is the only thing that changes `account::get_sequence_number(from)`).

### Finding Description
`transfer_from` builds the challenge struct and verifies it against a signature, but does not track or invalidate used nonces: [1](#0-0) 

The nonce field is populated from `account::get_sequence_number(from)`, i.e., the target account's live global transaction sequence number: [2](#0-1) 

`account::verify_signed_message` only checks that the supplied signature is valid over `message` with the account's *current* authentication key — it performs no bookkeeping of which `(address, nonce)` pairs have already been consumed, unlike the dedicated nonce/replay infrastructure elsewhere in the framework (`nonce_validation::check_and_insert_nonce`, used for orderless transactions): [3](#0-2) [4](#0-3) 

Crucially, `transfer_from` is invoked by `spender` (not by `from`), so calling it does **not** increment `from`'s account sequence number — only `from` submitting its own signed transactions does that. Therefore the value embedded in `expected_message.nonce` at call time is stable across repeated calls to `transfer_from` as long as `from` does not separately transact. An attacker who obtains one signed `Approval` (e.g., via an off-chain signing UI that leaks the raw signature, or a dApp that requests a single approval and stores it) can call `transfer_from` with the exact same `proof` bytes over and over; each call reconstructs the identical `expected_message` (same `nonce` because `from`'s sequence number hasn't moved) and the signature check passes every time, and `primary_fungible_store::transfer_with_ref` moves `amount` again on each call.

This is the direct custody analog of the EIP-4494 finding: the original bug was that `PositionManager`/`PermitERC721` failed to expose/implement per-token nonce tracking required by the standard, breaking the guarantee that a permit signature authorizes exactly one action. Here, the Aptos-native "permit" for fungible-asset transfer suffers the same root cause — nonce is declared as part of the signed message but is never consumed/incremented by the very function that is supposed to consume it — except the impact is direct, repeatable theft of custodied fungible-asset balance rather than an interface-compliance issue.

### Impact Explanation
This breaks the custody invariant that a single signed transfer authorization corresponds to a single, bounded transfer of value. Impact:
- Unauthorized, repeated withdrawal of `amount` units of `USDK` from `from`'s primary fungible store to `to`, executable by anyone who has ever seen one valid `proof` (the spender identity is bound into the message, but the "spender" signer itself is unprivileged and self-selectable per call as `signer::address_of(spender)` — the only thing fixed is which `spender` address was blessed in the original signed message, but that spender can call `transfer_from` as many times as desired).
- Because there is no on-chain state marking the approval as spent, this is not a rounding/edge case — it is a systemic drain: `from`'s entire discoverable balance can be extracted via repeated calls in the same or across many transactions, as long as `from`'s sequence number does not change.
- This corrupts custody accounting: value moves to `to`/`spender`'s control beyond what `from` actually authorized (a single transfer), which is precisely the "moves value to the wrong holder" custody-corruption category.

### Likelihood Explanation
High likelihood if this pattern is deployed as-is: exploitation requires no special privilege — only possession of a previously issued, still-signature-valid `proof`. Since real-world "approve once, use once" flows (e.g., a dApp requesting a one-time signed permit to pull funds) are exactly the scenario this function targets, any leaked or logged proof (client-side request logs, browser history, malicious frontend, mempool observation of a prior call, etc.) is directly replayable. The only mitigating factor is that `from`'s ordinary account activity (any of its own outgoing transactions) advances the sequence number and invalidates further replays — but a dormant or infrequently-active `from` account remains exposed indefinitely.

### Recommendation
- Do not use the account's live transaction `sequence_number` as an approval nonce; it is not consumed by this code path. Introduce a dedicated, module-owned nonce/table (or reuse `aptos_framework::nonce_validation`) per `(from, spender)` or per approval, and increment/mark it used *before* performing the transfer, atomically with the signature check.
- Alternatively, adopt a strictly single-use, monotonically-incrementing per-account "approval nonce" resource stored under the `stablecoin` module and require the caller to supply the expected next nonce, aborting if it doesn't match the stored value, then bumping it inside `transfer_from`.
- Add a deadline/expiration field (as EIP-2612/4494 do) to bound the validity window even after nonce fixes.

### Proof of Concept
1. `owner` (`from`) signs one `Approval { owner: from, to: attacker, nonce: account::get_sequence_number(from), chain_id, spender: attacker, amount: X }` intending to authorize a single transfer of `X` USDK to `attacker`, and shares `proof` with `attacker`'s dApp/service to execute the transfer once.
2. `attacker` calls `usdk::transfer_from(attacker_signer, proof, from, scheme, pubkey, attacker, X)`. This succeeds and moves `X` from `from` to `attacker`.
3. `attacker` calls `usdk::transfer_from` again with the identical `proof`/arguments. Because `from` has not submitted any transaction in the interim, `account::get_sequence_number(from)` is unchanged, so `expected_message` is byte-identical to what was signed, the signature check in `account::verify_signed_message` passes again, and another `X` is transferred.
4. Repeat step 3 until `from`'s balance is exhausted — no on-chain state prevents the replay, since `transfer_from` (lines 162-188 of `usdk.move`) contains no nonce-consumption or "already used" check.

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

**File:** aptos-move/framework/aptos-framework/sources/transaction_validation.move (L244-255)
```text
    fun check_for_replay_protection_orderless_txn(
        sender: address,
        nonce: u64,
        txn_expiration_time: u64,
    ) {
        // prologue_common already checks that the current_time > txn_expiration_time
        assert!(
            txn_expiration_time <= timestamp::now_seconds() + MAX_EXP_TIME_SECONDS_FOR_ORDERLESS_TXNS,
            error::invalid_argument(PROLOGUE_ETRANSACTION_EXPIRATION_TOO_FAR_IN_FUTURE),
        );
        assert!(nonce_validation::check_and_insert_nonce(sender, nonce, txn_expiration_time), error::invalid_argument(PROLOGUE_ENONCE_ALREADY_USED));
    }
```
