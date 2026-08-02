Confirmed: `account::get_sequence_number(addr)` simply reads `Account[addr].sequence_number` — it is only incremented by the transaction prologue/epilogue when `addr` itself is the **transaction sender** (`check_for_replay_protection_regular_txn` in `transaction_validation.move` bumps the sequence number tied to the sender/gas payer of a txn). In `usdk::transfer_from`, the `spender` (not `from`) is the transaction sender, so calling `transfer_from` never advances `from`'s sequence number.

### Title
Signed transfer approval in `usdk::transfer_from` is infinitely replayable, draining the owner's stablecoin balance - (File: `aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move`)

### Summary
`usdk::transfer_from` implements an ERC20-`permit`-like, off-chain-signed "approval" so a `spender` can move `amount` USDK from `from`'s primary store. The message's replay-protection field, `nonce`, is set to `account::get_sequence_number(from)` [1](#0-0) . This is the exact custody invariant that the external "unrevoked approval" report exploits in spirit: a one-time authorization is expected to become invalid after being consumed, but nothing here retires it.

### Finding Description
`Approval.nonce` is bound to `from`'s on-chain account sequence number [2](#0-1) . That counter is only incremented by the VM prologue/epilogue for the account that is the *transaction sender* — see `check_for_replay_protection_regular_txn`, which reads and validates `account::get_sequence_number(sender_address)` where `sender_address` is the signer of the enclosing transaction [3](#0-2) . Because `transfer_from` is invoked by `spender` (the transaction sender), not by `from`, `from`'s sequence number is untouched by this call. `account::verify_signed_message` performs pure signature verification against the supplied `message` struct and has no side effect that records or consumes anything — it does not mark the nonce as spent [4](#0-3) . Consequently the exact same `proof` bytes the owner signed once continue to satisfy `expected_message` on every subsequent call, and `primary_fungible_store::transfer_with_ref` executes again each time, moving `amount` out of `from`'s store using the module's privileged `TransferRef` [5](#0-4) . This is the "unrevoked approval" root cause from the external report reproduced in Aptos-native form: instead of a stale ERC20 allowance blocking future spends, a stale signed approval never expires and keeps re-authorizing spends, which is strictly worse (theft instead of DoS).

### Impact Explanation
Any account that once signs a `transfer_from` approval for `spender` (e.g., to pay for a single purchase) grants `spender` the ability to replay that identical approval indefinitely — draining `from`'s entire USDK primary-store balance in repeated `amount`-sized withdrawals, limited only by balance and by `from` itself submitting an unrelated transaction (which is the only thing that bumps their sequence number and invalidates the nonce). This is a direct custody violation: unauthorized transfer/theft of fungible-asset value held in a user's primary store, achievable purely by an unprivileged `spender` who was only ever authorized for a single transfer.

### Likelihood Explanation
High. No special privileges are required — a would-be attacker only needs one legitimate approval signed for any nonzero amount (a normal usage pattern such as a marketplace/payment checkout) and can then resubmit the same `proof`/parameters as many times as desired before `from` happens to send any transaction of their own.

### Recommendation
Do not reuse the account's global transaction sequence number as the nonce for an off-chain, module-specific approval. Maintain a dedicated per-owner (and ideally per-approval) nonce/counter inside the `usdk` module (or a `used_approvals: Table<vector<u8>, bool>` keyed by hash of the signed message) that is incremented/marked-used atomically inside `transfer_from` before or after the transfer succeeds, so the same signed message can never satisfy `verify_signed_message` twice.

### Proof of Concept
1. `owner` signs an `Approval { owner: from, to, nonce: account::get_sequence_number(from), chain_id, spender, amount }` once, e.g. authorizing a merchant to charge `amount` = 10 USDK.
2. `spender` calls `usdk::transfer_from(spender, proof, from, scheme, pubkey, to, amount)`. It succeeds, transferring 10 USDK.
3. `from` has sent no transaction, so `account::get_sequence_number(from)` is unchanged.
4. `spender` calls `transfer_from` again with the identical `proof`/parameters. `expected_message` recomputes to the same bytes, `verify_signed_message` succeeds again, and another 10 USDK is transferred.
5. Repeat until `from`'s balance is exhausted or `from` sends any transaction (which is the only event that increments their sequence number and breaks the replay). [6](#0-5) [3](#0-2)

### Citations

**File:** aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move (L160-188)
```text
    /// Allow a spender to transfer tokens from the owner's account given their signed approval.
    /// Caller needs to provide the from account's scheme and public key which can be gotten via the Aptos SDK.
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

**File:** aptos-move/framework/aptos-framework/sources/transaction_validation.move (L207-233)
```text
    fun check_for_replay_protection_regular_txn(
        sender_address: address,
        gas_payer_address: address,
        txn_sequence_number: u64,
    ) {
        if (
            sender_address == gas_payer_address
                || account::exists_at(sender_address)
                || !features::sponsored_automatic_account_creation_enabled()
                || txn_sequence_number > 0
        ) {
            assert!(account::exists_at(sender_address), error::invalid_argument(PROLOGUE_EACCOUNT_DOES_NOT_EXIST));
            let account_sequence_number = account::get_sequence_number(sender_address);
            assert!(
                txn_sequence_number < (1u64 << 63),
                error::out_of_range(PROLOGUE_ESEQUENCE_NUMBER_TOO_BIG)
            );

            assert!(
                txn_sequence_number >= account_sequence_number,
                error::invalid_argument(PROLOGUE_ESEQUENCE_NUMBER_TOO_OLD)
            );

            assert!(
                txn_sequence_number == account_sequence_number,
                error::invalid_argument(PROLOGUE_ESEQUENCE_NUMBER_TOO_NEW)
            );
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
