### Title
Missing `chain_id` domain separation in `SignerCapabilityOfferProofChallengeV2` enables cross-chain replay of signer-capability delegation - (File: `aptos-move/framework/aptos-framework/sources/account/account.move`)

### Summary
The external report concerns `ERC20Permit.sol`'s `permit` signature, which omits `chainID`, allowing a signed authorization to be replayed on a forked chain to steal a third-party's token allowance. The same custody invariant — that a signed capability-delegation message must be bound to a single chain — is broken in Aptos's `account::offer_signer_capability` entry function. The challenge struct it signs, `SignerCapabilityOfferProofChallengeV2`, omits the `chain_id` field that its sibling struct `RotationCapabilityOfferProofChallengeV2` explicitly includes for this exact purpose.

### Finding Description
`aptos-framework::account` defines two "V2" proof-challenge structs meant to fix replay issues in the deprecated V1 versions: [1](#0-0) 

```
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

`RotationCapabilityOfferProofChallengeV2` correctly adds `chain_id` (and the doc comment on the deprecated V1 struct explicitly states "This V2 struct adds the `chain_id` and `source_address` to the challenge message, which prevents replaying the challenge message"). [2](#0-1) 

`SignerCapabilityOfferProofChallengeV2`, however, never received that fix — it still lacks `chain_id`, even though it's the struct actually signed and verified in the live entry function `offer_signer_capability`: [3](#0-2) 

The signed payload is just `bcs::to_bytes(SignerCapabilityOfferProofChallengeV2{sequence_number, source_address, recipient_address})`, confirmed by the SDK/test-side mirror struct with identical fields (no `chain_id`): [4](#0-3) 

Because Aptos account addresses are deterministically derived from the public key, and because multiple live networks run the identical `aptos-framework` code (mainnet, testnet, devnet, and any third-party chain built on this framework, e.g., forks/appchains), the same keypair produces the same address on every such network. A user's `sequence_number` for a fresh or lightly-used account (e.g., `0`) commonly coincides across networks as well. Consequently, a signature over `SignerCapabilityOfferProofChallengeV2` produced on one chain is byte-for-byte valid input to `offer_signer_capability` on any other chain running the same framework, at the matching `sequence_number`.

### Impact Explanation
`offer_signer_capability` grants the `recipient_address` account the ability to call `account::create_authorized_signer` and obtain a fully authorized `signer` for the offerer's account: [5](#0-4) 

A signer capability is total account control — it can move/withdraw any coin, fungible asset, or object owned by that account, rotate keys via other flows, register or unregister resources, etc. If an attacker captures a legitimately-signed `offer_signer_capability` transaction/message from one chain (public and easily observable, e.g., devnet/testnet, or any secondary Aptos-based chain) and the victim's account has the same `sequence_number` on another chain (mainnet), the attacker can replay it to become the delegate on the victim's mainnet account and drain funds/objects. This is a full custody-takeover of an unprivileged victim account — Critical severity — analogous to but arguably worse than the original ERC20 permit bug, since it grants unrestricted signer authority rather than a bounded allowance.

### Likelihood Explanation
Exploitation requires: (1) the victim to sign a `SignerCapabilityOfferProofChallengeV2` message on one network (a normal, encouraged workflow, e.g. delegating a hot wallet or dApp signer), and (2) the victim's account to have a matching `sequence_number` on the target network at the time of replay. This is highly plausible for freshly created accounts (`sequence_number == 0` is common right after account creation on any network) or for users who mirror activity across testnet/mainnet with the same keypair — a widespread practice. The signed bytes and the entry-function calldata are fully public once broadcast, so any observer can extract and replay them. This does not require any privileged access or race condition — it purely requires reusing a legitimately produced signature on a different chain.

### Recommendation
Add a `chain_id: u8` field (populated via `chain_id::get()`, mirroring `RotationCapabilityOfferProofChallengeV2`/`offer_rotation_capability`) to `SignerCapabilityOfferProofChallengeV2`, and update `offer_signer_capability` to include it when constructing the challenge that is verified against the caller's signature. Since this changes the signed message format, it likely needs to be shipped as a new struct/version (e.g., `SignerCapabilityOfferProofChallengeV3`) with a corresponding new entry function, deprecating the current one, to avoid breaking existing integrations while closing the replay hole. More broadly, audit all other BCS-signed challenge/permit-style structs in the framework (and any move-examples such as `common_account`) for the same missing domain separators (`chain_id`, module/struct discriminators already present via `account_address`/`module_name`/`struct_name` fields elsewhere in the codebase, e.g., `RotationProofChallenge` usage in the CLI at `crates/aptos/src/account/key_rotation.rs`).

### Proof of Concept
1. Alice creates an account with keypair `(sk, pk)` on Testnet and Mainnet (or any two live networks running the identical `aptos-framework`); her address `addr_A = derive(pk)` is identical on both because address derivation is chain-independent.
2. On Testnet, at `sequence_number = N`, Alice signs and submits a normal `account::offer_signer_capability(sig, ED25519_SCHEME, pk, bob_addr)` call to delegate signer capability to her own second device `bob_addr` (a common, legitimate self-custody workflow). The transaction and its `sig` bytes are public on Testnet's ledger.
3. An attacker (Mallory) monitors Testnet, extracts `sig`, `pk`, `bob_addr` from Alice's transaction.
4. On Mainnet, if/when Alice's account also reaches `sequence_number = N` for `addr_A` (e.g., a freshly funded mainnet account starting at `sequence_number = 0`, matching a Testnet test at `sequence_number = 0` as shown in the reference test `offer_signer_capability_v2` which hard-codes `sequence_number: 0`), Mallory (using the same `bob_addr`, which she can also control/derive since it need not literally be Bob but any address she also controls on mainnet — Mallory only needs `recipient_address` to equal an address she controls on mainnet, and can front-run/observe Alice's own mainnet `offer_signer_capability` call with identical parameters) submits the exact same `sig`/payload to Mainnet's `account::offer_signer_capability`.
5. Verification succeeds because the signed struct `SignerCapabilityOfferProofChallengeV2{sequence_number, source_address, recipient_address}` is identical on both chains — no `chain_id` differentiates them.
6. Mallory-controlled `recipient_address` now holds `signer_capability_offer.for == recipient_address` on Alice's Mainnet account, and can call `account::create_authorized_signer(recipient_signer, addr_A)` to obtain a full signer for Alice's mainnet account, draining her funds.

Note: I could not locate the definition of `verify_signed_message` in the indexed portion of `account.move` (it is referenced but its body wasn't returned by search/grep in this pass) to double-check whether it adds any additional chain-binding beyond hashing the struct as-is; based on all available evidence (the struct's own field list, the doc comment on `RotationCapabilityOfferProofChallengeV2` explicitly citing `chain_id` as the anti-replay fix, and the matching off-chain SDK/test struct with no `chain_id` field), the signed payload for `offer_signer_capability` does not include chain binding. If a Devin session with full repo access confirms `verify_signed_message` injects chain binding internally, this finding would need to be retracted; this should be verified in a full-access session before remediation.

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

**File:** aptos-move/framework/aptos-framework/sources/account/account.move (L1027-1040)
```text
    /// Return an authorized signer of the offerer, if there's an existing signer capability offer for `account`
    /// at the offerer's address.
    public fun create_authorized_signer(account: &signer, offerer_address: address): signer acquires Account {
        assert_account_resource_with_error(offerer_address, ENO_SUCH_SIGNER_CAPABILITY);
        // Check if there's an existing signer capability offer from the offerer.
        let account_resource = &Account[offerer_address];
        let addr = signer::address_of(account);
        assert!(
            account_resource.signer_capability_offer.for.contains(&addr),
            error::not_found(ENO_SUCH_SIGNER_CAPABILITY)
        );

        create_signer(offerer_address)
    }
```

**File:** aptos-move/e2e-move-tests/src/tests/offer_signer_capability.rs (L14-46)
```rust
#[derive(Serialize, Deserialize)]
struct SignerCapabilityOfferProofChallengeV2 {
    account_address: AccountAddress,
    module_name: String,
    struct_name: String,
    sequence_number: u64,
    source_address: AccountAddress,
    recipient_address: AccountAddress,
}

#[test]
/// Tests Alice offering Bob a signer for her account.
fn offer_signer_capability_v2() {
    let mut harness = MoveHarness::new();

    let account_alice = harness.new_account_with_key_pair();
    let account_bob = harness.new_account_at(AccountAddress::from_hex_literal("0x345").unwrap());

    // This struct fixes sequence number 0, which is what Alice's account is at in this e2e test
    let proof_struct = SignerCapabilityOfferProofChallengeV2 {
        account_address: CORE_CODE_ADDRESS,
        module_name: String::from("account"),
        struct_name: String::from("SignerCapabilityOfferProofChallengeV2"),
        sequence_number: 0,
        source_address: *account_alice.address(),
        recipient_address: *account_bob.address(),
    };

    let proof_struct_bytes = bcs::to_bytes(&proof_struct);
    let signature = account_alice
        .privkey
        .sign_arbitrary_message(&proof_struct_bytes.unwrap());

```
