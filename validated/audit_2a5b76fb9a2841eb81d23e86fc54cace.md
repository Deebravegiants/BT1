### Title
Missing Caller Identity Binding in `verify_foreign_transaction` Enables Caller-Agnostic Root-Key Signature Issuance — (File: `crates/contract/src/lib.rs`)

---

### Summary

`MpcContract::verify_foreign_transaction` does not bind the caller's (`predecessor`) identity to the stored request, unlike `sign()` and `request_app_private_key()` which both embed the predecessor account ID into the request via tweak derivation. The stored `VerifyForeignTransactionRequest` contains no caller field, the response is signed against the **root** ForeignTx-domain public key (not a derived key), and the same response is fanned out to every NEAR account that submitted the identical request. Any unprivileged NEAR account can therefore obtain a valid MPC root-key signature over any foreign-chain transaction hash without owning or having any relationship to that transaction.

---

### Finding Description

**`sign()` and `request_app_private_key()` — caller identity is bound:**

`sign()` uses the returned `predecessor` to construct the request:

```rust
let request = SignatureRequest::new(
    request.domain_id,
    request.payload,
    &predecessor,       // ← caller baked into tweak
    &request.path,
);
``` [1](#0-0) 

`request_app_private_key()` does the same:

```rust
let request = CKDRequest::new(
    request.app_public_key,
    domain_id,
    &predecessor,       // ← caller baked into tweak
    &request.derivation_path,
);
``` [2](#0-1) 

**`verify_foreign_transaction()` — caller identity is silently discarded:**

`check_request_preconditions` returns `(domain_config, predecessor)`, but `verify_foreign_transaction` ignores the `predecessor`:

```rust
self.check_request_preconditions(   // return value discarded entirely
    request.domain_id,
    DomainPurpose::ForeignTx,
    ...
);
// predecessor is never used below
let request = args_into_verify_foreign_tx_request(request);
``` [3](#0-2) 

The resulting `VerifyForeignTransactionRequest` stored in `pending_verify_foreign_tx_requests` contains only `{request, domain_id, payload_version}` — no tweak, no predecessor: [4](#0-3) 

**`respond_verify_foreign_tx()` — signs with the root key, not a derived key:**

```rust
// Check the signature is correct against the root public key
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,           // ← root key, not derive_key_secp256k1(&affine, &tweak)
)
``` [5](#0-4) 

Compare with `respond()` for regular sign requests, which derives the expected key from the caller-specific tweak: [6](#0-5) 

**The fan-out is explicitly caller-agnostic:**

The test `verify_foreign_transaction__should_queue_duplicates_from_different_callers` confirms that Alice and Bob submitting the same request both receive the identical root-key `VerifyForeignTransactionResponse`: [7](#0-6) 

**Design intent vs. implementation gap:**

The design document explicitly planned caller-specific tweak derivation for this flow:

> `verify_foreign_transaction()` uses a **different tweak derivation prefix** than `sign()` so the same `(predecessor_id, derivation_path)` can never yield the same derived key across the two purposes. [8](#0-7) 

The planned `VerifyForeignTransactionRequestArgs` included `derivation_path` and the planned `VerifyForeignTransactionRequest` included a `tweak` field. Neither exists in the current production ABI or implementation. [9](#0-8) 

---

### Impact Explanation

**Impact: High** — Cross-chain verification bypass / invalid bridge execution.

Any unprivileged NEAR account can:

1. Observe a legitimate user's `verify_foreign_transaction` call on-chain (all NEAR transactions are public).
2. Submit the identical `VerifyForeignTransactionRequestArgs` (same `tx_id`, `chain`, `domain_id`).
3. Receive the same `VerifyForeignTransactionResponse` — a valid MPC root-key ECDSA signature over the foreign transaction's payload hash.
4. Present this response to a bridge contract **before the legitimate depositor does**, claiming the depositor's funds.

Because the response carries no caller identity and is signed with the root key (not a derived key tied to the depositor), a bridge contract that checks only signature validity and payload hash cannot distinguish the legitimate depositor from the front-runner. This enables double-spend / fund-theft conditions in any bridge built on top of `verify_foreign_transaction`.

---

### Likelihood Explanation

**Likelihood: Medium-High.**

- The attack requires no special privileges — any NEAR account with 1 yoctoNEAR can call `verify_foreign_transaction`.
- All NEAR transactions are publicly visible in real time; an attacker can observe and replay the exact same arguments within the same block or the next block.
- The fan-out behavior is already implemented and tested, so the contract will reliably deliver the response to the attacker's yield as well as the victim's.
- The only mitigation is a bridge contract independently re-binding the response to the depositor's identity — a burden the MPC contract was designed (per the doc) to handle itself.

---

### Recommendation

1. **Bind the caller's identity to the request**: include `predecessor_id` in `VerifyForeignTransactionRequest` (and in the map key), mirroring `SignatureRequest` and `CKDRequest`.
2. **Use a derived key, not the root key**: derive the signing key from `(root_key, tweak(predecessor_id, derivation_path))` with the `FOREIGN_TX_TWEAK_DERIVATION_PREFIX` already specified in the design doc, so the response is cryptographically tied to the requester.
3. **Add `derivation_path` to `VerifyForeignTransactionRequestArgs`**: this is already described in the design document and is the missing implementation step.

---

### Proof of Concept

```
1. Alice deposits 1 BTC to a bridge address on Bitcoin (tx_id = 0xABC...).

2. Alice calls verify_foreign_transaction({
       domain_id: ForeignTx_domain,
       payload_version: V1,
       request: Bitcoin { tx_id: 0xABC, confirmations: 6, extractors: [BlockHash] }
   }) with 1 yoctoNEAR deposit.
   → Alice's yield Y_alice is queued under key K = {request, domain_id, payload_version}.

3. Attacker Bob observes Alice's pending NEAR transaction on-chain.
   Bob calls verify_foreign_transaction with the IDENTICAL arguments.
   → Bob's yield Y_bob is also queued under the same key K.

4. MPC nodes verify the Bitcoin transaction, compute payload_hash, and call
   respond_verify_foreign_tx(request=K, response={payload_hash, root_key_sig}).
   → Both Y_alice and Y_bob are resolved with the same VerifyForeignTransactionResponse.

5. Bob's NEAR transaction completes first (or concurrently).
   Bob presents {payload_hash, root_key_sig} to the bridge contract.
   Bridge verifies: signature valid ✓, payload_hash matches tx_id 0xABC ✓.
   Bridge releases 1 BTC equivalent to Bob.

6. Alice's transaction also completes, but the bridge has already processed tx_id 0xABC.
   Alice's claim is rejected. Alice loses her 1 BTC deposit.
```

The root cause — `verify_foreign_transaction` discarding `predecessor` and storing a caller-agnostic key — is the direct necessary step enabling step 3 and 5. [10](#0-9) [11](#0-10)

### Citations

**File:** crates/contract/src/lib.rs (L379-384)
```rust
        let request = SignatureRequest::new(
            request.domain_id,
            request.payload,
            &predecessor,
            &request.path,
        );
```

**File:** crates/contract/src/lib.rs (L493-498)
```rust
        let request = CKDRequest::new(
            request.app_public_key,
            domain_id,
            &predecessor,
            &request.derivation_path,
        );
```

**File:** crates/contract/src/lib.rs (L519-557)
```rust
    pub fn verify_foreign_transaction(&mut self, request: VerifyForeignTransactionRequestArgs) {
        log!(
            "verify_foreign_transaction: predecessor={:?}, request={:?}",
            env::predecessor_account_id(),
            request
        );

        self.check_request_preconditions(
            request.domain_id,
            DomainPurpose::ForeignTx,
            Gas::from_tgas(self.config.sign_call_gas_attachment_requirement_tera_gas),
            MINIMUM_SIGN_REQUEST_DEPOSIT,
        );

        let requested_chain = request.request.chain();
        let supported_chains = self.get_supported_foreign_chains();
        if !supported_chains.contains(&requested_chain) {
            env::panic_str(
                &InvalidParameters::ForeignChainNotSupported {
                    requested: requested_chain,
                }
                .to_string(),
            );
        }

        let callback_gas = Gas::from_tgas(
            self.config
                .return_signature_and_clean_state_on_success_call_tera_gas,
        );

        let request = args_into_verify_foreign_tx_request(request);
        let callback_args = serde_json::to_vec(&(&request,)).unwrap();
        self.enqueue_yield_request(
            method_names::RETURN_VERIFY_FOREIGN_TX_AND_CLEAN_STATE_ON_SUCCESS,
            callback_args,
            callback_gas,
            move |this, id| this.add_verify_foreign_tx_request(request, id),
        );
    }
```

**File:** crates/contract/src/lib.rs (L597-608)
```rust
                let expected_public_key =
                    derive_key_secp256k1(&affine, &request.tweak).map_err(RespondError::from)?;

                let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");

                // Check the signature is correct
                near_mpc_signature_verifier::verify_ecdsa_signature(
                    signature_response,
                    payload_hash,
                    &expected_public_key,
                )
                .is_ok()
```

**File:** crates/contract/src/lib.rs (L718-734)
```rust
        let signature_is_valid = match (&response.signature, public_key) {
            (
                dtos::SignatureResponse::Secp256k1(signature_response),
                PublicKeyExtended::Secp256k1 { near_public_key },
            ) => {
                let secp_pk = dtos::Secp256k1PublicKey::try_from(&near_public_key)
                    .expect("Secp256k1 variant always has a secp256k1 key");

                let payload_hash: [u8; 32] = response.payload_hash.0;

                // Check the signature is correct against the root public key
                near_mpc_signature_verifier::verify_ecdsa_signature(
                    signature_response,
                    &payload_hash,
                    &secp_pk,
                )
                .is_ok()
```

**File:** crates/contract/src/lib.rs (L3208-3263)
```rust
    #[test]
    fn verify_foreign_transaction__should_queue_duplicates_from_different_callers() {
        // Given: two different callers will submit the same foreign-tx verification request.
        let mut rng = rand::rngs::StdRng::from_seed([42u8; 32]);
        let (context, mut contract, secret_key) =
            basic_setup_with_protocol(Protocol::CaitSith, DomainPurpose::ForeignTx, &mut rng);
        register_supported_chains(&mut contract, [dtos::ForeignChain::Bitcoin]);
        let SharedSecretKey::Secp256k1(secret_key) = secret_key else {
            unreachable!();
        };

        let request_args = VerifyForeignTransactionRequestArgs {
            domain_id: DomainId::default().0.into(),
            payload_version: ForeignTxPayloadVersion::V1,
            request: dtos::ForeignChainRpcRequest::Bitcoin(BitcoinRpcRequest {
                tx_id: [7u8; 32].into(),
                confirmations: 2.into(),
                extractors: vec![BitcoinExtractor::BlockHash],
            }),
        };
        let request = args_into_verify_foreign_tx_request(request_args.clone());

        // When: caller alice submits the request.
        let alice = AccountId::from_str("alice.near").unwrap();
        testing_env!(
            VMContextBuilder::new()
                .signer_account_id(alice.clone())
                .predecessor_account_id(alice)
                .current_account_id(context.current_account_id.clone())
                .attached_deposit(NearToken::from_yoctonear(1))
                .build()
        );
        contract.verify_foreign_transaction(request_args.clone());

        // And: caller bob submits the identical request — a different account would today
        // be blocked from receiving a response by alice's submission.
        let bob = AccountId::from_str("bob.near").unwrap();
        testing_env!(
            VMContextBuilder::new()
                .signer_account_id(bob.clone())
                .predecessor_account_id(bob)
                .current_account_id(context.current_account_id.clone())
                .attached_deposit(NearToken::from_yoctonear(1))
                .build()
        );
        contract.verify_foreign_transaction(request_args);

        // Then: both yields are queued under the single (caller-agnostic) request key.
        assert_eq!(
            contract
                .pending_verify_foreign_tx_requests
                .get(&request)
                .map(|q| q.len()),
            Some(2),
            "duplicate foreign-tx requests from different callers should fan out",
        );
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L124-128)
```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```

**File:** docs/foreign-chain-transactions.md (L98-111)
```markdown
pub struct VerifyForeignTransactionRequestArgs {
    pub request: ForeignChainRpcRequest,
    pub derivation_path: String, // Key derivation path
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}

pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub tweak: Tweak,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```
```

**File:** docs/foreign-chain-transactions.md (L254-286)
```markdown
## Tweak Derivation (Sign vs ForeignTx)

`verify_foreign_transaction()` uses a **different tweak derivation prefix** than `sign()` so the same
`(predecessor_id, derivation_path)` can never yield the same derived key across the two purposes.

Design:

* Keep the existing sign tweak derivation prefix unchanged.
* Introduce a foreign-tx-specific prefix and derive the tweak from the same `(predecessor_id, derivation_path)`
  input using the same hash construction.
* The contract derives the tweak internally from `request.derivation_path` (callers do not submit raw tweaks).

Example:

```rust
const SIGN_TWEAK_DERIVATION_PREFIX: &str =
    "near-mpc-recovery v0.1.0 epsilon derivation:";
const FOREIGN_TX_TWEAK_DERIVATION_PREFIX: &str =
    "near-mpc-recovery v0.1.0 foreign-tx epsilon derivation:";

pub fn derive_sign_tweak(predecessor_id: &AccountId, path: &str) -> Tweak {
    let hash: [u8; 32] = derive_from_path(SIGN_TWEAK_DERIVATION_PREFIX, predecessor_id, path);
    Tweak::new(hash)
}

pub fn derive_foreign_tx_tweak(predecessor_id: &AccountId, path: &str) -> Tweak {
    let hash: [u8; 32] = derive_from_path(FOREIGN_TX_TWEAK_DERIVATION_PREFIX, predecessor_id, path);
    Tweak::new(hash)
}
```

This ensures key material used for validated foreign transactions is **always** distinct from
general-purpose `sign()` keys, even if the same account and derivation path are reused.
```
