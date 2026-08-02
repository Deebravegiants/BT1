Confirmed: `account::verify_signed_message` at [1](#0-0)  only checks that the signature matches the account's current auth key against the arbitrary message struct — it performs no state mutation, no nonce consumption, and no on-chain tracking of "used" messages. The `chain_id` and `sequence_number` fields are only replay-resistant if the embedding module actually ties them to a value that changes as a result of the call itself.

### Title
`usdk::transfer_from` signed-approval replay: `nonce` is the owner's account sequence number, which `transfer_from` never advances, allowing unlimited replay of a single approval - (File: `aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move`)

### Summary
The USDK stablecoin example implements an ERC20-`permit`-style meta-transfer, `transfer_from`, which lets a `spender` move funds out of an `owner`'s account using an off-chain signed `Approval` message instead of the owner submitting the transaction. This is the closest Aptos analog to the RabbitHole `mintReceipt` bug class: a custody-relevant action is authorized purely by a signed message, and replay-safety of that message hinges entirely on how the "nonce" is chosen and consumed.

### Finding Description
`transfer_from` builds the `Approval` challenge using `nonce: account::get_sequence_number(from)`: [2](#0-1) 

The `from` account's on-chain sequence number is only incremented when `from` itself submits a transaction (normal Aptos transaction prologue/epilogue). `transfer_from` is called by `spender`, not `from` — `from` is passed only as a plain `address` argument and never signs or submits this transaction. Consequently:
- The `nonce` embedded in the `Approval` struct does not change as a side effect of calling `transfer_from`.
- `account::verify_signed_message` itself performs no bookkeeping to mark a message as "consumed"; it is a pure boolean-verification call against the current auth key [1](#0-0) .
- Therefore, the exact same `proof` bytes produced by `from` for a given `(to, amount, spender)` tuple remain valid and can be submitted by `spender` repeatedly, draining `amount` from `from` on every replay, until `from` happens to submit any ordinary transaction of its own (which increments its sequence number and invalidates the signature).

This mirrors the RabbitHole bug class precisely: a custody-affecting operation (asset transfer, analogous to minting the receipt) is authorized by a signature whose "nonce" is not tied to consumption of that very authorization, so the same signed message can be replayed multiple times for repeated unauthorized value movement.

### Impact Explanation
Because the FA store transfer moves real custody of the stablecoin from `from` to `to` via `primary_fungible_store::transfer_with_ref` using the module's privileged `TransferRef` [3](#0-2) , a single approval signed by `owner` for a spender/amount can be replayed by the spender to repeatedly withdraw `amount` from `owner`'s balance in successive transactions, well beyond what the owner intended to authorize. This is a custody-grade impact: unauthorized, repeated draining of a user's fungible-asset balance controlled by a resource with live custody authority (`TransferRef`).

### Likelihood Explanation
This requires no privileged assumption beyond a user (`from`) signing one legitimate `Approval` off-chain and a malicious or compromised `spender` (or anyone who intercepts the signed `proof`, since it's passed as a plain argument in a public entry-adjacent function) resubmitting it. Because ordinary Aptos users can go long periods without submitting transactions themselves (their sequence number is otherwise static), the exploit window can be large. Note this file lives under `aptos-move/move-examples/`, i.e., example/reference code rather than the core deployed framework, which lowers real-world mainnet exposure since it is not itself a deployed system contract — it would only be impactful for any project that copies this pattern verbatim into production.

### Recommendation
Use a dedicated, monotonically-incrementing (or one-time) nonce stored in a resource owned by the `usdk` module (or by `owner`), incremented/consumed atomically inside `transfer_from` itself, rather than relying on the account's global sequence number which is unaffected by this call. Additionally consider adding an explicit expiration timestamp to the `Approval` struct.

### Proof of Concept
1. `owner` signs `Approval { owner, to, nonce: account::get_sequence_number(owner), chain_id, spender, amount }` off-chain and gives `proof` to `spender` for a single intended transfer.
2. `spender` calls `usdk::transfer_from(spender, proof, owner, scheme, pubkey, to, amount)` — succeeds, funds move.
3. `spender` calls `usdk::transfer_from` again with the identical `proof` — `account::get_sequence_number(owner)` is unchanged (since `owner` never submitted a transaction), so the reconstructed `Approval` matches, `verify_signed_message` succeeds again, and `amount` is withdrawn a second time.
4. Repeat until `owner`'s balance is exhausted or `owner` submits any transaction (which bumps its sequence number and finally invalidates the signature).

### Citations

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
