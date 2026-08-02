## Finding

The reported bug class ("signature can be replayed because the authorized amount is never invalidated after use") reduces to one custody invariant: **an off-chain-signed spending authorization must be single-use (or explicitly capped), and its freshness must be tied to state that changes as a *direct result* of that authorization being consumed.**

Searching Aptos-native custody flows (object/FA/multisig/resource-account/signature-verification code) for the same class, the strongest analog is in the `usdk` stablecoin example's ERC20-style `transfer_from` "permit" flow, which reimplements the exact pattern the external report warns about — a signed approval for a specific `(from, to, spender, amount)` — but binds its freshness to the wrong piece of state.

### Title
Replayable `transfer_from` approval signature due to nonce bound to the wrong account's sequence number - (File: `aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move`)

### Summary
`usdk::transfer_from` lets a `spender` move `amount` of the owner's (`from`'s) fungible-asset balance by presenting an `Approval` message signed by `from`. The "nonce" embedded in that message is `account::get_sequence_number(from)`, but the transaction that consumes the approval is submitted and sequenced by `spender`, not by `from`. Because `from`'s own sequence number is only advanced when `from` is the *sender* of a transaction [1](#0-0) , an approval signed once by `from` remains valid for every subsequent call as long as `from` does not independently submit a transaction that happens to bump its sequence number to the value in the message.

### Finding Description
`transfer_from` constructs the challenge and verifies it against `from`'s public key: [2](#0-1) 

The nonce field is `account::get_sequence_number(from)` [3](#0-2) . Nothing in `transfer_from` (or anywhere reachable from it) increments `from`'s `Account.sequence_number` — that field lives in the `Account` resource and is only mutated by the VM prologue/epilogue for the transaction's actual sender [4](#0-3) [5](#0-4) . Since `spender` (not `from`) is the signer/sender of the `transfer_from` transaction, `from`'s sequence number is untouched by this call. This breaks the same invariant the external report describes for `createSigner`: the authorization contains an "amount control" field, but nothing forces it to be single-use, so it becomes a standing, indefinitely reusable withdrawal authorization once leaked or shared (e.g., through a relayer, secondary market for approvals, or simple accidental reuse by the dApp itself).

This is architecturally different from Aptos's own properly-designed nonce-bound signature flows, which the framework gets right elsewhere:
- `RotationProofChallenge` explicitly documents why binding to the transaction's own sequence number prevents replay [6](#0-5) , and the on-chain state (`Account.authentication_key`/mapping) changes as a direct effect of consuming the challenge, invalidating stale challenges automatically [7](#0-6) .
- `multisig_account` transaction execution is keyed by an incrementing `sequence_number` per multisig account that is explicitly advanced/removed by execution, and votes are looked up per-sequence-number in a table, so an approval can't be replayed against a later transaction [8](#0-7) .

`usdk::transfer_from` copies the *shape* of a nonce (a `u64` field labeled "nonce") without wiring it to state that actually advances when the authorization is used, defeating the intended replay protection.

### Impact Explanation
Any `spender` who obtains one valid `Approval` signature from `from` for amount `A` can call `transfer_from` repeatedly, draining `A` tokens from `from`'s primary fungible store every time, up to `from`'s full balance, with no re-authorization required. This is a direct custody break: unauthorized, repeated movement of fungible-asset value out of an unprivileged owner's store, exactly the "theft of fungible asset held value via broken authorization" category. Because `from`'s sequence number is essentially decoupled from this action, in the common case where `from` is a passive signer (e.g., a user who only ever interacts through gasless/relayed `transfer_from` calls and never submits transactions themselves), the nonce is static forever and the signature is trivially and indefinitely replayable — worse than the classic ERC-20 `permit` bugs since there isn't even an incrementing per-owner "approvals nonce" tracked by this module, unlike, e.g., OpenZeppelin's `ERC20Permit`.

### Likelihood Explanation
High. Exploitation requires no privileged access — any party that legitimately receives one `Approval` signature from an owner (e.g., a relayer, marketplace, or the spender itself) can replay it. No special conditions are needed beyond the owner not submitting an unrelated transaction that happens to consume the identical nonce value (which for a typical off-chain relayed user is unlikely to ever happen before the signature is reused).

### Recommendation
Do not derive the nonce from `account::get_sequence_number(from)`. Instead:
- Maintain a dedicated, module-owned per-owner (or per-owner-per-spender) nonce counter (e.g., a `Table<address, u64>` in `Management`/`State`) that `transfer_from` increments atomically as part of consuming the approval, or
- Store a `Table<vector<u8> /* hash of Approval */, bool>` of used approvals and assert-and-set it before the transfer executes, mirroring how `multisig_account` binds votes to a specific incrementing `sequence_number` that execution consumes.

### Proof of Concept
1. `from` signs an `Approval{ owner: from, to, nonce: account::get_sequence_number(from) /* e.g. 5 */, chain_id, spender, amount }` off-chain and gives the signature `proof` to `spender` (e.g., via a gasless relay UI), intending to authorize one transfer of `amount`.
2. `spender` calls `usdk::transfer_from(spender, proof, from, scheme, pubkey, to, amount)`. `account::get_sequence_number(from)` still returns `5` (unchanged, since `from` was not the transaction sender), so verification succeeds and `amount` moves from `from` to `to`.
3. `spender` calls `usdk::transfer_from` again with the same `proof`. `from`'s sequence number is still `5` (no transaction of `from`'s has been processed), so the exact same signature verifies again, and another `amount` is transferred.
4. Step 3 repeats until `from`'s balance is exhausted, with `from` never having authorized more than a single `amount` transfer.

Note: this finding is scoped to the `move-examples/fungible_asset/stablecoin` reference module rather than the core `aptos-framework` — I could not find an equivalent signature-replay flaw inside the core mainnet framework's own custody paths (`account.move`, `multisig_account.move`, `fungible_asset.move`, `object.move`), which all correctly bind signature freshness to state that changes as a direct effect of consuming the signature. If this `usdk` module (or an unmodified derivative of it) is deployed as-is by a stablecoin issuer, the vulnerability is fully live on mainnet.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/transaction_validation.move (L169-185)
```text
        // Check for replay protection
        match (replay_protector) {
            SequenceNumber(txn_sequence_number) => {
                check_for_replay_protection_regular_txn(
                    sender_address,
                    gas_payer_address,
                    txn_sequence_number,
                );
            },
            Nonce(nonce) => {
                check_for_replay_protection_orderless_txn(
                    sender_address,
                    nonce,
                    txn_expiration_time,
                );
            }
        };
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

**File:** aptos-move/framework/aptos-framework/sources/account/account.move (L60-69)
```text
    /// Resource representing an account.
    struct Account has key, store {
        authentication_key: vector<u8>,
        sequence_number: u64,
        guid_creation_num: u64,
        coin_register_events: EventHandle<CoinRegisterEvent>,
        key_rotation_events: EventHandle<KeyRotationEvent>,
        rotation_capability_offer: CapabilityOffer<RotationCapability>,
        signer_capability_offer: CapabilityOffer<SignerCapability>,
    }
```

**File:** aptos-move/framework/aptos-framework/sources/account/account.move (L117-131)
```text
    /// This structs stores the challenge message that should be signed during key rotation. First, this struct is
    /// signed by the account owner's current public key, which proves possession of a capability to rotate the key.
    /// Second, this struct is signed by the new public key that the account owner wants to rotate to, which proves
    /// knowledge of this new public key's associated secret key. These two signatures cannot be replayed in another
    /// context because they include the TXN's unique sequence number.
    struct RotationProofChallenge has copy, drop {
        sequence_number: u64,
        // the sequence number of the account whose key is being rotated
        originator: address,
        // the address of the account whose key is being rotated
        current_auth_key: address,
        // the current authentication key of the account whose key is being rotated
        new_public_key: vector<u8>,
        // the new public key that the account owner wants to rotate to
    }
```

**File:** aptos-move/framework/aptos-framework/sources/account/account.move (L654-710)
```text
    public entry fun rotate_authentication_key(
        account: &signer,
        from_scheme: u8,
        from_public_key_bytes: vector<u8>,
        to_scheme: u8,
        to_public_key_bytes: vector<u8>,
        cap_rotate_key: vector<u8>,
        cap_update_table: vector<u8>,
    ) acquires Account, OriginatingAddress {
        let addr = signer::address_of(account);
        ensure_resource_exists(addr);
        let account_resource = &mut Account[addr];
        let old_auth_key = account_resource.authentication_key;
        // Verify the given `from_public_key_bytes` matches this account's current authentication key.
        if (from_scheme == ED25519_SCHEME) {
            let from_pk = ed25519::new_unvalidated_public_key_from_bytes(from_public_key_bytes);
            let from_auth_key = ed25519::unvalidated_public_key_to_authentication_key(&from_pk);
            assert!(
                account_resource.authentication_key == from_auth_key,
                error::unauthenticated(EWRONG_CURRENT_PUBLIC_KEY)
            );
        } else if (from_scheme == MULTI_ED25519_SCHEME) {
            let from_pk = multi_ed25519::new_unvalidated_public_key_from_bytes(from_public_key_bytes);
            let from_auth_key = multi_ed25519::unvalidated_public_key_to_authentication_key(&from_pk);
            assert!(
                account_resource.authentication_key == from_auth_key,
                error::unauthenticated(EWRONG_CURRENT_PUBLIC_KEY)
            );
        } else {
            abort error::invalid_argument(EINVALID_SCHEME)
        };

        // Construct a valid `RotationProofChallenge` that `cap_rotate_key` and `cap_update_table` will validate against.
        let curr_auth_key_as_address = from_bcs::to_address(account_resource.authentication_key);
        let challenge = RotationProofChallenge {
            sequence_number: account_resource.sequence_number,
            originator: addr,
            current_auth_key: curr_auth_key_as_address,
            new_public_key: to_public_key_bytes,
        };

        // Assert the challenges signed by the current and new keys are valid
        assert_valid_rotation_proof_signature_and_get_auth_key(
            from_scheme,
            from_public_key_bytes,
            cap_rotate_key,
            &challenge
        );
        let new_auth_key = assert_valid_rotation_proof_signature_and_get_auth_key(
            to_scheme,
            to_public_key_bytes,
            cap_update_table,
            &challenge
        );

        // Update the `OriginatingAddress` table.
        update_auth_key_and_originating_address_table(addr, account_resource, new_auth_key);
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1328-1353)
```text
    fun validate_multisig_transaction(
        owner: &signer, multisig_account: address, payload: vector<u8>) {
        assert_multisig_account_exists(multisig_account);
        assert_is_owner(owner, multisig_account);
        let sequence_number = last_resolved_sequence_number(multisig_account) + 1;
        assert_transaction_exists(multisig_account, sequence_number);

        if (features::multisig_v2_enhancement_feature_enabled()) {
            assert!(
                can_execute(address_of(owner), multisig_account, sequence_number),
                error::invalid_argument(ENOT_ENOUGH_APPROVALS),
            );
        }
        else {
            assert!(
                can_be_executed(multisig_account, sequence_number),
                error::invalid_argument(ENOT_ENOUGH_APPROVALS),
            );
        };

        // Count approvals, including the executing owner's implicit vote.
        let (num_approvals, _) = num_approvals_and_rejections(multisig_account, sequence_number);
        if (!has_voted_for_approval(multisig_account, sequence_number, address_of(owner))) {
            num_approvals += 1;
        };
        assert!(num_approvals >= num_signatures_required(multisig_account), error::invalid_argument(ENOT_ENOUGH_APPROVALS));
```
