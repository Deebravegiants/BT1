## Custody Invariant Reduction

The external report's core invariant: **a signed authorization message must be scoped (domain-separated) to the specific chain/application it targets, or it becomes replayable elsewhere.**

Aptos analog candidates considered:
1. `multisig_account` creation messages — include `chain_id` + `account_address`, properly scoped. Rejected.
2. Object address derivation (`OBJECT_DERIVED_SCHEME`, `DERIVE_RESOURCE_ACCOUNT_SCHEME`) — scheme-tagged hashes, not signature-replay relevant. Rejected.
3. `RotationCapabilityOfferProofChallengeV2` — explicitly includes `chain_id` "to prevent replaying the challenge message" [1](#0-0) . Properly scoped. Rejected.
4. `SignerCapabilityOfferProofChallengeV2` used by `account::offer_signer_capability` — **no `chain_id` field**, unlike its rotation-capability sibling. Kept as strongest candidate.

### Title
Missing `chain_id` in `SignerCapabilityOfferProofChallengeV2` enables cross-chain signer-capability replay leading to full account takeover - (File: `aptos-move/framework/aptos-framework/sources/account/account.move`)

### Summary
`account::offer_signer_capability` verifies a signed `SignerCapabilityOfferProofChallengeV2` struct containing only `sequence_number`, `source_address`, and `recipient_address` [2](#0-1) . Its sibling struct, `RotationCapabilityOfferProofChallengeV2`, was explicitly upgraded to add a `chain_id` field with the documented purpose of preventing challenge-message replay [1](#0-0) , but the equivalent hardening was never applied to `SignerCapabilityOfferProofChallengeV2`.

### Finding Description
`offer_signer_capability` builds the challenge from only account-local state and verifies it via `verify_signed_message`, which checks the signature against the account's authentication key with no chain-scoping input at all [3](#0-2) ; the underlying `verify_signed_message<T>` generic function itself has no notion of `chain_id` — it only checks the auth key and the raw signature over the caller-supplied struct `T` [4](#0-3) .

Because Aptos account addresses are derived deterministically from the public key (identical across mainnet, testnet, devnet, and any other Aptos-compatible chain using the same account module), a user who signs a `SignerCapabilityOfferProofChallengeV2` on one chain (e.g., testnet, or a chain with the same module) produces BCS-identical bytes to what they would sign for the *same* `source_address`/`recipient_address`/`sequence_number` triple on a different chain. If that recipient address and sequence number coincide on another Aptos-based network (a very plausible scenario for freshly created accounts at `sequence_number = 0`, or for any deliberately crafted matching state by an attacker who controls the recipient account), the signature is valid and replayable there, since no chain identifier is baked into the signed payload.

### Impact Explanation
A successful replay lets the attacker (holder of `recipient_address`) call `create_authorized_signer` to obtain a fully-privileged `signer` for the victim's account on the second chain (grep confirms `create_authorized_signer` consumes the `signer_capability_offer.for` field set by `offer_signer_capability`). Holding a full account `signer` is complete custody takeover: the attacker can transfer all APT/fungible-asset balances, move or burn owned objects, rotate the auth key, or drain any resource under that address — a critical, non-recoverable custody loss.

### Likelihood Explanation
Exploitation requires: (a) the victim signs an `offer_signer_capability` message intended for one Aptos-based chain, (b) the same `source_address` exists with matching `sequence_number` on another chain the attacker also controls/monitors, and (c) the attacker registers/controls the same `recipient_address` there. Because addresses are public-key derived and identical across networks, and `sequence_number = 0` is common for new accounts, this is realistically triggerable, but it is not a zero-interaction attack — it depends on cross-chain address/sequence coincidence and predictable recipient targeting, which lowers likelihood somewhat relative to the original LGO bug but does not eliminate it.

### Recommendation
Add a `chain_id` field to `SignerCapabilityOfferProofChallengeV2` (mirroring the fix already applied to `RotationCapabilityOfferProofChallengeV2`), bump to a V3 struct, and update `offer_signer_capability` to populate and require it, consistent with `chain_id::get()` usage elsewhere in the module.

### Proof of Concept
Conceptual (illustrating the missing field, not a full replay harness):
```move
// Current (vulnerable) struct — no chain scoping:
struct SignerCapabilityOfferProofChallengeV2 has copy, drop {
    sequence_number: u64,
    source_address: address,
    recipient_address: address,
}

// Sibling struct that WAS hardened against replay:
struct RotationCapabilityOfferProofChallengeV2 has drop {
    chain_id: u8,
    sequence_number: u64,
    source_address: address,
    recipient_address: address,
}
```
An attacker who obtains a `signer_capability_sig_bytes` signed by Alice for `offer_signer_capability(source=Alice, recipient=Bob, sequence_number=N)` on Chain A can resubmit the identical bytes to `offer_signer_capability` on Chain B for the same `(Alice, Bob, N)` triple; `verify_signed_message` will accept it since nothing in the signed struct differs between chains, after which `create_authorized_signer` yields Bob a full signer for Alice's Chain-B account.

**Note on verification limits:** I could not execute this in a live multi-network environment to empirically confirm replay success end-to-end (e.g., confirm `sequence_number` alignment assumptions or check if any out-of-band chain-id enforcement exists at the VM/transaction level for this specific entry function); the analysis is based on static code inspection of `account.move` only. A Devin session with sandbox execution could construct a concrete two-network Move test to confirm exploitability with certainty.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/account/account.move (L145-153)
```text
    /// This struct stores the challenge message that should be signed by the source account, when the source account
    /// is delegating its rotation capability to the `recipient_address`.
    /// This V2 struct adds the `chain_id` and `source_address` to the challenge message, which prevents replaying the challenge message.
    struct RotationCapabilityOfferProofChallengeV2 has drop {
        chain_id: u8,
        sequence_number: u64,
        source_address: address,
        recipient_address: address,
    }
```

**File:** aptos-move/framework/aptos-framework/sources/account/account.move (L155-159)
```text
    struct SignerCapabilityOfferProofChallengeV2 has copy, drop {
        sequence_number: u64,
        source_address: address,
        recipient_address: address,
    }
```

**File:** aptos-move/framework/aptos-framework/sources/account/account.move (L954-977)
```text
    public entry fun offer_signer_capability(
        account: &signer,
        signer_capability_sig_bytes: vector<u8>,
        account_scheme: u8,
        account_public_key_bytes: vector<u8>,
        recipient_address: address
    ) acquires Account {
        let source_address = signer::address_of(account);
        ensure_resource_exists(source_address);
        assert!(exists_at(recipient_address), error::not_found(EACCOUNT_DOES_NOT_EXIST));

        // Proof that this account intends to delegate its signer capability to another account.
        let proof_challenge = SignerCapabilityOfferProofChallengeV2 {
            sequence_number: get_sequence_number(source_address),
            source_address,
            recipient_address,
        };
        verify_signed_message(
            source_address, account_scheme, account_public_key_bytes, signer_capability_sig_bytes, proof_challenge);

        // Update the existing signer capability offer or put in a new signer capability offer for the recipient.
        let account_resource = &mut Account[source_address];
        account_resource.signer_capability_offer.for.swap_or_fill(recipient_address);
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
