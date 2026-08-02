## Custody Analog Found: Missing Chain-ID Domain Separation in `RotationProofChallenge` Enables Cross-Network Auth-Key-Rotation Signature Replay

### Title
Missing chain-id domain separation in `account::RotationProofChallenge` allows off-chain rotation signatures to be replayed across different Aptos-derived networks, enabling unauthorized account/auth-key takeover — (File: `aptos-move/framework/aptos-framework/sources/account/account.move`)

### Summary
The external report's root custody invariant is: *a value used to authorize/validate an action must be bound to the specific deployed instance (chain/contract) it was created for; if it is not, a signature or message valid in one instance can be replayed in another instance that shares the same code, silently granting unauthorized control.* In `MechMarketplace` this was `domainSeparator` baked in at constructor time and shared across proxies. The Aptos analog is `RotationProofChallenge`, the struct signed off-chain to authorize account authentication-key rotation, which — unlike its sibling `RotationCapabilityOfferProofChallengeV2` — omits `chain_id`, breaking domain separation across distinct chain instances that share the same Move framework code and address-derivation scheme.

### Finding Description
`RotationProofChallenge` is defined with only `sequence_number`, `originator`, `current_auth_key`, and `new_public_key`: [1](#0-0) 

The comment claims replay-safety solely from the sequence number ("cannot be replayed in another context because they include the TXN's unique sequence number"), which is a same-chain assumption; it does not hold across two different Aptos-derived chain deployments (e.g., devnet/testnet vs. mainnet, or any two networks sharing the framework module address `0x1`) where the same account address can independently exist with the same `sequence_number` (commonly `0` for a fresh account) and same `current_auth_key`.

Contrast this with `RotationCapabilityOfferProofChallengeV2`, whose own doc comment explicitly states the fix for exactly this class of bug — "This V2 struct adds the `chain_id` ... which prevents replaying the challenge message": [2](#0-1) 

`RotationProofChallenge` is signed independently by both the current and new key and verified via `assert_valid_rotation_proof_signature_and_get_auth_key`/`signature_verify_strict_t`, which serializes only `TypeInfo` (module address/name/struct name — identical across chains since `0x1` is the same on every Aptos network) plus the struct fields — again no chain-specific salt: [3](#0-2) [4](#0-3) 

The corrupted invariant: the challenge message intended to authorize a rotation "in this specific chain context" is actually valid in any chain context sharing the same account address, sequence number, and current auth key — i.e., the "domain" (chain) is not part of the signed message, exactly mirroring the shared-`domainSeparator`-across-proxies flaw in the external report.

### Impact Explanation
Authentication-key rotation is the Aptos-native equivalent of full ownership reassignment of an account and everything it custodies (APT, objects, fungible-asset stores, resource-account signer capabilities reachable from that account, etc.). If an attacker observes/collects a legitimately-signed `RotationProofChallenge` pair (e.g., a user rotates keys on a devnet/testnet clone of the framework, or on any secondary chain sharing this module) and the same account address on the mainnet instance has not yet diverged (sequence number/auth key still match), the attacker can submit that exact signature pair to rotate the mainnet account's key to one they control — a critical, non-recoverable custody takeover with no privileged role required beyond capturing a previously broadcast/observed signature.

### Likelihood Explanation
Exploitation requires: (1) the victim to have produced a valid `RotationProofChallenge` signature pair in some chain context (this happens routinely for legitimate key-rotation flows, wallet migrations, etc.), and (2) an address/sequence-number/auth-key match on another chain instance running the same framework code. Because Aptos account addresses are derived purely from the public key (independent of chain), and fresh accounts on any new chain start at `sequence_number = 0`, this condition is realistically satisfiable for any account that has rotated keys early in its lifecycle on one network before transacting on another. This is lower likelihood than a fully generic on-chain bug (it needs signature interception across networks) but is directly analogous in root cause to the reported class and does not depend on leaked private keys — only on reusing a legitimately produced, publicly observable signed message.

### Recommendation
Add `chain_id: u8` (as already done for `RotationCapabilityOfferProofChallengeV2`) to `RotationProofChallenge`, and thread `chain_id::get()` into its construction sites in `rotate_authentication_key` and `rotate_authentication_key_with_rotation_capability`, so that a rotation signature is cryptographically bound to the specific chain it was authorized for.

### Proof of Concept
Conceptual reproduction (would need to be run against two chain deployments sharing the same framework module, e.g. two local `aptos node run-local-testnet` genesis instances):
1. Create account `A` (address derived from public key `pk`) on Chain 1 and Chain 2, both starting at `sequence_number = 0` with `current_auth_key = A`.
2. On Chain 1, have the true owner rotate `A`'s key from `pk` to `pk_new` by signing `RotationProofChallenge { sequence_number: 0, originator: A, current_auth_key: A, new_public_key: pk_new }` with both `sk` (current) and `sk_new` (new), producing `sig_curr` and `sig_new`.
3. On Chain 2 (mainnet-equivalent), where `A` still has `sequence_number = 0` and `current_auth_key = A` and has not rotated, an attacker submits `rotate_authentication_key(ED25519_SCHEME, pk, ED25519_SCHEME, pk_new, sig_curr, sig_new)` on behalf of `A`.
4. Because `RotationProofChallenge` contains no `chain_id`, verification in `assert_valid_rotation_proof_signature_and_get_auth_key` succeeds on Chain 2 using the Chain-1-signed message, rotating `A`'s auth key to `pk_new` without the Chain-2 owner's consent. [5](#0-4)

### Citations

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

**File:** aptos-move/framework/aptos-framework/sources/account/account.move (L1056-1080)
```text
    fun assert_valid_rotation_proof_signature_and_get_auth_key(
        scheme: u8,
        public_key_bytes: vector<u8>,
        signature: vector<u8>,
        challenge: &RotationProofChallenge
    ): vector<u8> {
        if (scheme == ED25519_SCHEME) {
            let pk = ed25519::new_unvalidated_public_key_from_bytes(public_key_bytes);
            let sig = ed25519::new_signature_from_bytes(signature);
            assert!(
                ed25519::signature_verify_strict_t(&sig, &pk, *challenge),
                std::error::invalid_argument(EINVALID_PROOF_OF_KNOWLEDGE)
            );
            ed25519::unvalidated_public_key_to_authentication_key(&pk)
        } else if (scheme == MULTI_ED25519_SCHEME) {
            let pk = multi_ed25519::new_unvalidated_public_key_from_bytes(public_key_bytes);
            let sig = multi_ed25519::new_signature_from_bytes(signature);
            assert!(
                multi_ed25519::signature_verify_strict_t(&sig, &pk, *challenge),
                std::error::invalid_argument(EINVALID_PROOF_OF_KNOWLEDGE)
            );
            multi_ed25519::unvalidated_public_key_to_authentication_key(&pk)
        } else {
            abort error::invalid_argument(EINVALID_SCHEME)
        }
```

**File:** aptos-move/framework/aptos-framework/sources/account/account.move (L1861-1882)
```text
            originator: alice_addr,
            current_auth_key: alice_addr,
            new_public_key: multi_ed25519::unvalidated_public_key_to_bytes(&new_pk_unvalidated),
        };

        let from_sig = multi_ed25519::sign_struct(&curr_sk, challenge);
        let to_sig = multi_ed25519::sign_struct(&new_sk, challenge);

        rotate_authentication_key(
            &alice,
            MULTI_ED25519_SCHEME,
            multi_ed25519::unvalidated_public_key_to_bytes(&curr_pk_unvalidated),
            MULTI_ED25519_SCHEME,
            multi_ed25519::unvalidated_public_key_to_bytes(&new_pk_unvalidated),
            multi_ed25519::signature_to_bytes(&from_sig),
            multi_ed25519::signature_to_bytes(&to_sig),
        );
        let address_map = &OriginatingAddress[@aptos_framework].address_map;
        let expected_originating_address = address_map.borrow(new_address);
        assert!(*expected_originating_address == alice_addr, 0);
        assert!(Account[alice_addr].authentication_key == new_auth_key, 0);
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
