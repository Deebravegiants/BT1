### Title
Missing chain ID in `SignerCapabilityOfferProofChallengeV2` allows cross-chain signature replay to hijack account signer capability - (File: `aptos-move/framework/aptos-framework/sources/account/account.move`)

### Summary
`account::offer_signer_capability()` authorizes delegation of full signer capability over a user's account based on a signature over `SignerCapabilityOfferProofChallengeV2`. Unlike its sibling struct `RotationCapabilityOfferProofChallengeV2`, which was explicitly patched to add a `chain_id` field "to prevent replaying the challenge message," `SignerCapabilityOfferProofChallengeV2` was never given the same fix and still lacks a `chain_id` field. A signature authorizing a signer-capability delegation on one Aptos chain (e.g., testnet/devnet, or any chain sharing the same account address, sequence number, and auth key) can be replayed verbatim on another chain (e.g., mainnet) to grant an attacker-controlled recipient full signer capability over the victim's mainnet account.

### Finding Description
`account.move` defines two "V2" proof-challenge structs used to authorize delegation of sensitive account capabilities: [1](#0-0) 

The `RotationCapabilityOfferProofChallengeV2` struct includes a `chain_id` field, and the code comment explicitly states this field "prevents replaying the challenge message" — confirming that the Aptos team recognized cross-chain replay as a threat and patched it for this struct. However, `SignerCapabilityOfferProofChallengeV2`, defined immediately below it, has no `chain_id` field at all.

This asymmetry carries through into the actual usage:

- `offer_rotation_capability()` builds its challenge with `chain_id: chain_id::get()`: [2](#0-1) 

- `offer_signer_capability()` builds its challenge with **no chain_id**, using only `sequence_number`, `source_address`, and `recipient_address`, then calls `verify_signed_message`: [3](#0-2) 

The underlying signature verification (`ed25519::signature_verify_strict_t` / `verify_signed_message`) wraps the challenge in a `SignedMessage<T>` that only binds `type_info` (module/struct name) and the struct's own fields — it does not inject any chain identifier: [4](#0-3) 

Because `SignerCapabilityOfferProofChallengeV2` omits `chain_id`, an off-chain signature over this struct is valid on **any** Aptos-compatible chain where the same `source_address`, `sequence_number`, and public key state exist — which is common in practice (fresh accounts at sequence number 0, forked/duplicate networks, or accidental key reuse across mainnet/testnet/devnet by the same user or wallet software).

### Impact Explanation
`signer_capability_offer.for` grants the named recipient the ability to obtain a full `&signer` for the offering account (via `account::create_authorized_signer`), which is equivalent to complete custody control: the recipient can transfer all coins/fungible assets, rotate the authentication key, publish modules under the account, and perform any other authenticated action as if they were the account owner. A replay of a benign delegation signed for a low-stakes/test environment onto mainnet results in unauthorized, permanent takeover of a live account's assets and control — satisfying the "unauthorized takeover of ... multisig control, resource-account control ... tied to live assets" and "theft ... of APT, fungible assets" custody-impact criteria. This is High/Critical severity because it results in full account compromise with no on-chain recovery path once the malicious `offer_signer_capability` transaction executes and the recipient extracts the signer capability.

### Likelihood Explanation
Exploitation requires only that the same account address/keys/sequence-number state exist on two chains that both run this framework version (e.g., mainnet vs. testnet/devnet, or a forked/duplicate chain). This is a realistic condition because: (1) wallets and CLIs frequently reuse the same private key across mainnet/testnet, (2) freshly created accounts on either network typically start at sequence number 0, and (3) the attacker only needs to intercept or otherwise obtain a signature the victim produced for a "harmless" test-network delegation and rebroadcast it (via `offer_signer_capability`) against the victim's mainnet account. No privileged access or governance action is needed — any third party who obtains the signed bytes can submit the replay transaction.

### Recommendation
Add a `chain_id: u8` field to `SignerCapabilityOfferProofChallengeV2` (mirroring the fix already applied to `RotationCapabilityOfferProofChallengeV2`), populate it with `chain_id::get()` in `offer_signer_capability()`, and require any client/SDK that constructs this struct to include the corresponding chain ID. This closes the domain-separation gap and prevents replay of signer-capability delegation signatures across chains.

### Proof of Concept
1. Victim Alice controls the same private key/address on both Testnet (chain_id = T) and Mainnet (chain_id = M), with account sequence number `n` and auth key `AK` identical on both networks (realistic for a newly bootstrapped account or reused test key).
2. Alice signs a `SignerCapabilityOfferProofChallengeV2 { sequence_number: n, source_address: Alice, recipient_address: Bob }` intending to delegate signer capability to Bob on Testnet only, and submits `account::offer_signer_capability(...)` on Testnet.
3. Because the struct has no `chain_id`, the exact same `signer_capability_sig_bytes` is valid input to `offer_signer_capability` on Mainnet as well, since `Account[Alice].sequence_number == n` and `Account[Alice].authentication_key == AK` still hold there.
4. An attacker (or Bob himself) submits `account::offer_signer_capability(Alice, signer_capability_sig_bytes, account_scheme, account_public_key_bytes, Bob)` on Mainnet. Verification in `verify_signed_message`/`signature_verify_strict_t` succeeds because it checks only the BCS-serialized struct fields and type info, not the chain.
5. `Account[Alice].signer_capability_offer.for` is now set to Bob's Mainnet address. Bob calls `account::create_authorized_signer(bob_signer, Alice)` to obtain a full `&signer` for Alice's Mainnet account and drains/transfers all of Alice's mainnet assets.

Note: I was unable to execute this end-to-end in a live environment; this analysis is based on static review of the `account.move` module, comparing the (patched) `RotationCapabilityOfferProofChallengeV2` against the (unpatched) `SignerCapabilityOfferProofChallengeV2`, and tracing `offer_signer_capability`'s reliance on `ed25519::signature_verify_strict_t`, which does not incorporate chain context. A background Devin session with repo/test access would be needed to confirm exact preconditions (e.g., whether `verify_signed_message` performs any hidden chain check elsewhere) and to build a full harness-based PoC.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/account/account.move (L145-159)
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

    struct SignerCapabilityOfferProofChallengeV2 has copy, drop {
        sequence_number: u64,
        source_address: address,
        recipient_address: address,
    }
```

**File:** aptos-move/framework/aptos-framework/sources/account/account.move (L822-829)
```text
        // proof that this account intends to delegate its rotation capability to another account
        let account_resource = &mut Account[addr];
        let proof_challenge = RotationCapabilityOfferProofChallengeV2 {
            chain_id: chain_id::get(),
            sequence_number: account_resource.sequence_number,
            source_address: addr,
            recipient_address,
        };
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

**File:** aptos-move/framework/aptos-stdlib/sources/cryptography/ed25519.move (L140-149)
```text
    /// This function is used to verify a signature on any BCS-serializable type T. For now, it is used to verify the
    /// proof of private key ownership when rotating authentication keys.
    public fun signature_verify_strict_t<T: drop>(signature: &Signature, public_key: &UnvalidatedPublicKey, data: T): bool {
        let encoded = SignedMessage {
            type_info: type_info::type_of<T>(),
            inner: data,
        };

        signature_verify_strict_internal(signature.bytes, public_key.bytes, bcs::to_bytes(&encoded))
    }
```
