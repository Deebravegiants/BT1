## Custody Analog Found: Struct Field-Layout Collision Enables Cross-Message Signature Reuse Between `MultisigAccountCreationMessage` and `MultisigAccountCreationWithAuthKeyRevocationMessage`

### Title
Identical field layout between `MultisigAccountCreationMessage` and `MultisigAccountCreationWithAuthKeyRevocationMessage` may allow a signature intended for non-destructive migration to force irreversible auth-key revocation - (File: `aptos-move/framework/aptos-framework/sources/multisig_account.move`)

### Summary
The external report's core defect is a **type-hash/struct-field mismatch that lets a signature validated for one semantic meaning be reused/misapplied for a different, more dangerous operation**. The closest Aptos-native analog I found is in `multisig_account.move`, where two distinct proof-challenge structs used to authorize different on-chain actions have **byte-for-byte identical field layouts**: [1](#0-0) 

```
struct MultisigAccountCreationMessage has copy, drop {
    chain_id: u8,
    account_address: address,
    sequence_number: u64,
    owners: vector<address>,
    num_signatures_required: u64,
}

struct MultisigAccountCreationWithAuthKeyRevocationMessage has copy, drop {
    chain_id: u8,
    account_address: address,
    sequence_number: u64,
    owners: vector<address>,
    num_signatures_required: u64,
}
```

### Finding Description
Both `create_with_existing_account` (non-destructive migration) and `create_with_existing_account_and_revoke_auth_key` (destructive — zeroes the auth key) build their respective proof-challenge struct from identical caller-supplied inputs and pass it to `account::verify_signed_message`: [2](#0-1) [3](#0-2) 

Move's BCS serialization (`bcs::to_bytes`) encodes only field values in declaration order — it embeds **no struct/type name** in the byte stream, unlike the Rust-side `CryptoHash` derive macros used elsewhere in the codebase, which explicitly add a type-based salt for domain separation: [4](#0-3) 

Because `MultisigAccountCreationMessage` and `MultisigAccountCreationWithAuthKeyRevocationMessage` have exactly the same field types/order, their BCS-serialized bytes are identical for the same input values. If the signature verification path (`ed25519::signature_verify_strict_t` / `multi_ed25519::signature_verify_strict_t`, called from `account::verify_signed_message`) does not itself inject a type-name/domain-separation tag before hashing the message, a signature an account owner produces over a `MultisigAccountCreationMessage` (intending the *non-destructive* migration path) would also validate as a signature over `MultisigAccountCreationWithAuthKeyRevocationMessage` for the same `(chain_id, account_address, sequence_number, owners, num_signatures_required)` tuple — allowing anyone in possession of that signature to call `create_with_existing_account_and_revoke_auth_key` instead of the intended `create_with_existing_account`.

This mirrors exactly the class of bug in the external report: the verification struct used to check a signature does not match, in a security-relevant way, what the signer actually intended to authorize.

**Important caveat on verification confidence:** I was not able to read the full implementation body of `account::verify_signed_message` or `ed25519::signature_verify_strict_t`/`multi_ed25519::signature_verify_strict_t` before running out of tool iterations, so I could not directly confirm whether these native/library functions add their own type-tag domain separation on top of raw BCS bytes (e.g., via `type_info::type_of<T>()` prefixing) that would neutralize this collision. The finding rests on: (1) the two structs' field layouts being provably identical in source, and (2) BCS itself carrying no type information — both directly verified in code. Whether an additional domain-separation layer exists inside the signature-verification natives is **unconfirmed** and should be checked before treating this as exploitable.

### Impact Explanation
If the collision is real, an attacker who intercepts (or is given) a signature intended for `create_with_existing_account` can instead submit it to `create_with_existing_account_and_revoke_auth_key`. This:
- Forces `account::rotate_authentication_key_internal(multisig_account, ZERO_AUTH_KEY)`, permanently zeroing the original account's auth key — an irreversible loss of key-based control.
- Also strips any existing rotation/signer capability offers (`account::revoke_any_signer_capability`, `account::revoke_any_rotation_capability`), removing all alternate recovery paths.
- For accounts that hold APT, fungible assets, or serve as resource-account signers, this permanently locks out the original owner's ability to control the account via their private key, with recovery only possible through the newly (and now sole) multisig governance structure — a non-recoverable custody-control change the original signer did not consent to.

### Likelihood Explanation
Likelihood depends entirely on whether the signature-verification native functions add domain separation beyond raw BCS bytes. This is unconfirmed in this session. If they do not, the likelihood is high: no privileged access is needed — any party who has legitimately obtained (or observed, since these functions take a signature as a public calldata argument) a validly-signed `MultisigAccountCreationMessage` for a given account can replay it against the revocation entry function.

### Recommendation
1. Confirm whether `ed25519::signature_verify_strict_t` / `multi_ed25519::signature_verify_strict_t` (or `account::verify_signed_message`) prepend a type-name/domain tag to the serialized message before verification.
2. If they do not, add an explicit discriminant field (e.g., a `revoke_auth_key: bool` field, or a distinct constant/enum tag) to both `MultisigAccountCreationMessage` and `MultisigAccountCreationWithAuthKeyRevocationMessage` so their serialized byte streams can never collide.
3. As defense in depth, audit all other "proof challenge" structs signed via `account::verify_signed_message` across `account.move` (e.g., `RotationProofChallenge`, `SignerCapabilityOfferProofChallengeV2`) for identical field-layout collisions with other challenge structs used for different-consequence operations.

### Proof of Concept
Not executable — this requires confirming, inside `ed25519.move`/`multi_ed25519.move`, whether `signature_verify_strict_t<T>` embeds any type-specific salt before hashing `bcs::to_bytes(&data)`. A concrete PoC would: (1) have an account owner sign a `MultisigAccountCreationMessage{chain_id, account_address, sequence_number, owners, num_signatures_required}`, (2) submit that exact signature to `create_with_existing_account_and_revoke_auth_key` with the same field values, and (3) observe whether `account::verify_signed_message` accepts it, resulting in unintended auth-key zeroing. This step could not be completed within the available tool budget.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L207-235)
```text
    /// Used only for verifying multisig account creation on top of existing accounts.
    struct MultisigAccountCreationMessage has copy, drop {
        // Chain id is included to prevent cross-chain replay.
        chain_id: u8,
        // Account address is included to prevent cross-account replay (when multiple accounts share the same auth key).
        account_address: address,
        // Sequence number is not needed for replay protection as the multisig account can only be created once.
        // But it's included to ensure timely execution of account creation.
        sequence_number: u64,
        // The list of owners for the multisig account.
        owners: vector<address>,
        // The number of signatures required (signature threshold).
        num_signatures_required: u64,
    }

    /// Used only for verifying multisig account creation on top of existing accounts and rotating the auth key to 0x0.
    struct MultisigAccountCreationWithAuthKeyRevocationMessage has copy, drop {
        // Chain id is included to prevent cross-chain replay.
        chain_id: u8,
        // Account address is included to prevent cross-account replay (when multiple accounts share the same auth key).
        account_address: address,
        // Sequence number is not needed for replay protection as the multisig account can only be created once.
        // But it's included to ensure timely execution of account creation.
        sequence_number: u64,
        // The list of owners for the multisig account.
        owners: vector<address>,
        // The number of signatures required (signature threshold).
        num_signatures_required: u64,
    }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L632-647)
```text
        // Verify that the `MultisigAccountCreationMessage` has the right information and is signed by the account
        // owner's key.
        let proof_challenge = MultisigAccountCreationMessage {
            chain_id: chain_id::get(),
            account_address: multisig_address,
            sequence_number: account::get_sequence_number(multisig_address),
            owners,
            num_signatures_required,
        };
        account::verify_signed_message(
            multisig_address,
            account_scheme,
            account_public_key,
            create_multisig_account_signed_message,
            proof_challenge,
        );
```

**File:** crates/aptos-crypto/src/hash.rs (L613-641)
```rust
/// The default hasher underlying generated implementations of `CryptoHasher`.
#[doc(hidden)]
#[derive(Clone)]
pub struct DefaultHasher {
    state: Sha3,
}

impl DefaultHasher {
    #[doc(hidden)]
    /// This function does not return a HashValue in the sense of our usual
    /// hashes, but a construction of initial bytes that are fed into any hash
    /// provided we're passed  a (bcs) serialization name as argument.
    pub fn prefixed_hash(buffer: &[u8]) -> [u8; HashValue::LENGTH] {
        // The salt is initial material we prefix to actual value bytes for
        // domain separation. Its length is variable.
        let salt: Vec<u8> = [HASH_PREFIX, buffer].concat();
        // The seed is a fixed-length hash of the salt, thereby preventing
        // suffix attacks on the domain separation bytes.
        HashValue::sha3_256_of(&salt[..]).hash
    }

    #[doc(hidden)]
    pub fn new(typename: &[u8]) -> Self {
        let mut state = Sha3::v256();
        if !typename.is_empty() {
            state.update(&Self::prefixed_hash(typename));
        }
        DefaultHasher { state }
    }
```
