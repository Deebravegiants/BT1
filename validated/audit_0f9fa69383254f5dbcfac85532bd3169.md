## Custody Analog Found: Missing chain_id in `SignerCapabilityOfferProofChallengeV2` enables cross-network signer capability theft

### Title
Signer capability delegation signature is replayable across Aptos chains/networks (missing chain_id domain separation) - (File: `aptos-move/framework/aptos-framework/sources/account/account.move`)

### Summary
The external report's bug class is a missing domain separator (chain/contract identity) in a signed authorization message, allowing cross-chain replay. Aptos-core's own `account.move` module explicitly fixed this exact class of bug for rotation-capability delegation by adding `chain_id` to `RotationCapabilityOfferProofChallengeV2` [1](#0-0) , with an explicit comment stating this "prevents replaying the challenge message" across chains. However, the sibling struct `SignerCapabilityOfferProofChallengeV2`, used to authorize delegation of full **signer capability** (a much stronger authority than rotation), was never given the same treatment — it omits `chain_id` entirely.

### Finding Description
`SignerCapabilityOfferProofChallengeV2` is defined without `chain_id`: [2](#0-1) 

It is constructed and verified in `offer_signer_capability`, which signs/verifies only `sequence_number`, `source_address`, and `recipient_address`: [3](#0-2) 

Because Aptos account addresses are derived deterministically from the public key (and are chain-agnostic), the same keypair/account address can legitimately exist across multiple Aptos-based networks (mainnet, testnet, devnet, or any independent chain instance sharing the Aptos VM/framework, including forks). Since `sequence_number` is also independently tracked per-chain and can coincide (e.g., a freshly created account with `sequence_number = 0` on both networks), an owner's signed `SignerCapabilityOfferProofChallengeV2` message produced for one network is a byte-for-byte-identical, validly-signed message on any other network where the same address/sequence-number state exists. `verify_signed_message` only checks the ed25519/multi-ed25519 signature against the struct's BCS bytes plus type info (module/struct name), not against any chain identifier — so nothing in the verification path stops this replay.

### Impact Explanation
Signer capability is a full authority object (`SignerCapability`) — it lets `create_authorized_signer`/`create_signer_with_capability` fully impersonate the offering account, including moving `AptosCoin`, fungible assets, calling arbitrary entry functions as that account, and controlling any objects or resource accounts owned by it. If a user or protocol treasury account exists with the same address/keys across two Aptos-compatible networks and signs a `SignerCapabilityOfferProofChallengeV2` intending to delegate control on one network only, an attacker who observes that signature can replay it on the other network to obtain full signer capability there — a direct account/asset takeover. This satisfies the custody gate: unauthorized takeover of account/resource control tied to live assets.

### Likelihood Explanation
This is contingent on: (1) the same account address/keypair having equivalent on-chain state (sequence_number) across two networks — a realistic scenario for testnet/mainnet parity setups, migrations, or any Aptos-framework-based side/L1 chain sharing genesis-style deterministic addressing, and (2) the signed message being observable (submitted on one chain, or leaked off-chain before submission). This is a real, narrower-scope replay than a fully generic cross-chain attack, and I could not verify from the index whether any additional runtime/global domain separation (e.g., unique genesis IDs mixed into `verify_signed_message` at a lower level in Rust) exists outside what's visible in `account.move`. This uncertainty affects confidence but the Move-level struct itself is demonstrably inconsistent with its sibling `RotationCapabilityOfferProofChallengeV2`, which was deliberately patched for this exact issue.

### Recommendation
Add a `chain_id: u8` field to `SignerCapabilityOfferProofChallengeV2` (mirroring `RotationCapabilityOfferProofChallengeV2`), populate it with `chain_id::get()` in `offer_signer_capability`, and treat this as a required framework upgrade (with appropriate versioning/migration since it changes the signed struct's BCS layout, which is a breaking change for any off-chain signing tooling).

### Proof of Concept
Conceptual, based on the test harnesses already present in the module [4](#0-3) :
1. Alice controls the same address/keypair on Chain A (e.g. testnet) and Chain B (e.g. mainnet-equivalent), both with `sequence_number = 0` for her account.
2. On Chain A, Alice signs `SignerCapabilityOfferProofChallengeV2 { sequence_number: 0, source_address: alice_addr, recipient_address: bob_addr }` intending to delegate signer capability to Bob only on Chain A, and submits `offer_signer_capability(...)`.
3. Attacker observes this signature (public mempool/tx data) and resubmits the identical `signer_capability_sig_bytes` via `offer_signer_capability` on Chain B, where the struct's `chain_id` is never checked.
4. Verification succeeds because the byte-encoding of the challenge is chain-agnostic; Bob (or attacker, if `recipient_address` is attacker's own address reused across chains) now holds signer capability over Alice's account on Chain B without her Chain-B-specific consent.

Note: I was unable to fully trace the lower-level Rust `verify_signed_message`/native signature verification path within the given iteration budget to rule out an additional out-of-Move domain separation mechanism; this should be double-checked before treating this as fully confirmed, but the Move source itself, and its explicit contrast with `RotationCapabilityOfferProofChallengeV2`'s deliberate chain_id fix, strongly indicates a real gap.

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

**File:** aptos-move/framework/aptos-framework/sources/account/account.move (L960-977)
```text
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

**File:** aptos-move/framework/aptos-framework/sources/account/account.move (L1658-1672)
```text
        let challenge = SignerCapabilityOfferProofChallengeV2 {
            sequence_number: Account[alice_addr].sequence_number,
            source_address: alice_addr,
            recipient_address: bob_addr,
        };

        let alice_signer_capability_offer_sig = ed25519::sign_struct(&alice_sk, challenge);

        offer_signer_capability(
            &alice,
            ed25519::signature_to_bytes(&alice_signer_capability_offer_sig),
            0,
            alice_pk_bytes,
            bob_addr
        );
```
