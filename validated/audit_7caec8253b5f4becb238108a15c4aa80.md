### Title
Caller Identity Not Bound in `verify_foreign_transaction`, Allowing Any Account to Obtain Root-Key Signatures Over Arbitrary Foreign-Chain Transactions - (File: crates/contract/src/lib.rs)

---

### Summary

The `verify_foreign_transaction` method in `MpcContract` discards the caller's account identity when constructing the pending request. Unlike `sign()` and `request_app_private_key()`, which both embed `predecessor_account_id` into the request key (creating a per-caller key derivation tweak), `verify_foreign_transaction` constructs a `VerifyForeignTransactionRequest` with no caller binding. Any unprivileged account can submit a verification request for any foreign-chain transaction ID and receive a valid **root-key** MPC signature over that transaction's data.

---

### Finding Description

**Inconsistency with sibling request methods:**

`sign()` binds the request to the caller:

```rust
// crates/contract/src/lib.rs:379-384
let request = SignatureRequest::new(
    request.domain_id,
    request.payload,
    &predecessor,      // ← caller identity baked into tweak
    &request.path,
);
```

`request_app_private_key()` does the same:

```rust
// crates/contract/src/lib.rs:493-498
let request = CKDRequest::new(
    request.app_public_key,
    domain_id,
    &predecessor,      // ← caller identity baked in
    &request.derivation_path,
);
```

`verify_foreign_transaction()` **silently discards** the predecessor returned by `check_request_preconditions`:

```rust
// crates/contract/src/lib.rs:526-531
self.check_request_preconditions(   // return value (domain_config, predecessor) DISCARDED
    request.domain_id,
    DomainPurpose::ForeignTx,
    Gas::from_tgas(self.config.sign_call_gas_attachment_requirement_tera_gas),
    MINIMUM_SIGN_REQUEST_DEPOSIT,
);
// ...
let request = args_into_verify_foreign_tx_request(request);  // no predecessor included
```

`args_into_verify_foreign_tx_request` simply copies the three caller-agnostic fields:

```rust
// crates/contract/src/dto_mapping.rs:840-848
pub fn args_into_verify_foreign_tx_request(
    args: dtos::VerifyForeignTransactionRequestArgs,
) -> dtos::VerifyForeignTransactionRequest {
    dtos::VerifyForeignTransactionRequest {
        domain_id: args.domain_id,
        request: args.request,
        payload_version: args.payload_version,
    }
}
```

The `VerifyForeignTransactionRequest` struct itself carries no caller field:

```rust
// crates/near-mpc-contract-interface/src/types/foreign_chain.rs:124-128
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```

**Signing uses the root key, not a per-caller derived key:**

`respond_verify_foreign_tx` verifies the signature against the **root public key** (no tweak applied), confirmed at lines 718–743 of `crates/contract/src/lib.rs`. This means the resulting `VerifyForeignTransactionResponse` is a root-key attestation over the foreign-chain transaction data, not scoped to any particular caller.

**Fan-out is confirmed and intentional:**

The test at `crates/contract/src/lib.rs:3208–3298` explicitly confirms that two different callers (Alice and Bob) submitting the same request both receive the same root-key signature from a single MPC response. The comment at line 3255 reads: *"both yields are queued under the single (caller-agnostic) request key."*

**The SDK verifier does not check caller identity:**

`ForeignChainSignatureVerifier.verify_signature()` in `crates/near-mpc-sdk/src/foreign_chain.rs:42–89` only checks:
1. The payload hash matches expected extracted values
2. The ECDSA/EdDSA signature is valid against the root public key

It performs no check that the entity presenting the `VerifyForeignTransactionResponse` is the same entity that originally submitted the `verify_foreign_transaction` call.

---

### Impact Explanation

An attacker can call `verify_foreign_transaction` for any foreign-chain transaction ID (e.g., a Bitcoin or Ethereum deposit transaction targeting a bridge contract) and receive a valid root-key MPC signature over that transaction's data. Because `ForeignChainSignatureVerifier.verify_signature()` only validates cryptographic correctness and not caller identity, the attacker can present this signature to any bridge contract that accepts a `VerifyForeignTransactionResponse` as proof of a foreign-chain event.

Concretely:
- A bridge contract designed to release NEAR-side funds upon receiving a valid MPC attestation of a foreign-chain deposit can be drained by an attacker who independently calls `verify_foreign_transaction` for the victim's deposit transaction, receives the root-key signature, and presents it to the bridge contract's claim function before or alongside the legitimate user.
- Because the request key is caller-agnostic, the attacker's yield and the legitimate user's yield are queued under the same map entry and both resolved by a single MPC response — the attacker receives an identical, valid signature.

This constitutes **cross-chain replay / invalid bridge execution**: the attacker obtains a genuine MPC root-key attestation for a transaction they did not originate and uses it to trigger unauthorized fund release.

---

### Likelihood Explanation

The attack requires only:
1. A 1 yoctoNEAR deposit (the `MINIMUM_SIGN_REQUEST_DEPOSIT`)
2. Sufficient prepaid gas
3. Knowledge of the target foreign-chain transaction ID (publicly visible on-chain)

No privileged access, threshold collusion, or key material is needed. Any NEAR account can execute this against any bridge contract that uses `verify_foreign_transaction` without caller-binding its own claim logic.

---

### Recommendation

1. **Bind the request to the caller's identity** in `verify_foreign_transaction`, mirroring `sign()` and `request_app_private_key()`. Include `predecessor_account_id` in `VerifyForeignTransactionRequest` (or derive a per-caller tweak) so that the resulting signature is scoped to the submitting account.

2. **Update `ForeignChainSignatureVerifier.verify_signature()`** in the SDK to accept and validate a caller-identity field, so bridge contracts can confirm the response was produced for their specific invocation.

3. **Add documentation** warning that `verify_foreign_transaction` currently produces caller-agnostic root-key signatures, and that bridge contracts must not accept externally-supplied `VerifyForeignTransactionResponse` values as authorization without additional caller-binding checks.

---

### Proof of Concept

```
Setup:
  - BridgeContract: a NEAR contract that calls verify_foreign_transaction(bitcoin_tx_id=X)
    and, upon receiving a valid VerifyForeignTransactionResponse, releases 10 NEAR to
    whoever presents it via a separate claim(response) entry point.
  - Victim: legitimate depositor who sent BTC to the bridge's Bitcoin address (tx_id = X).
  - Attacker: any NEAR account.

Step 1: Attacker observes tx_id X on Bitcoin (public mempool/chain).

Step 2: Attacker calls:
  mpc_contract.verify_foreign_transaction({
    domain_id: <foreign_tx_domain>,
    payload_version: V1,
    request: BitcoinRpcRequest { tx_id: X, confirmations: 2, extractors: [BlockHash] }
  }, deposit=1 yoctoNEAR)

Step 3: MPC nodes verify tx X on Bitcoin, sign the payload with the root key,
  and resolve the attacker's yield with VerifyForeignTransactionResponse { payload_hash, signature }.

Step 4: Attacker's callback receives the valid root-key signature.

Step 5: Attacker calls BridgeContract.claim(response=<attacker's VerifyForeignTransactionResponse>).

Step 6: BridgeContract calls ForeignChainSignatureVerifier.verify_signature(response, root_public_key).
  → Passes: signature is cryptographically valid, payload hash matches tx X.
  → BridgeContract releases 10 NEAR to the attacker.

Result: Victim's Bitcoin deposit is consumed; attacker receives the NEAR-side funds.
  The victim's subsequent verify_foreign_transaction call also succeeds (fan-out),
  but the bridge funds are already drained.
```

**Root cause lines:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** crates/contract/src/lib.rs (L526-531)
```rust
        self.check_request_preconditions(
            request.domain_id,
            DomainPurpose::ForeignTx,
            Gas::from_tgas(self.config.sign_call_gas_attachment_requirement_tera_gas),
            MINIMUM_SIGN_REQUEST_DEPOSIT,
        );
```

**File:** crates/contract/src/dto_mapping.rs (L840-848)
```rust
pub fn args_into_verify_foreign_tx_request(
    args: dtos::VerifyForeignTransactionRequestArgs,
) -> dtos::VerifyForeignTransactionRequest {
    dtos::VerifyForeignTransactionRequest {
        domain_id: args.domain_id,
        request: args.request,
        payload_version: args.payload_version,
    }
}
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L124-128)
```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```

**File:** crates/near-mpc-sdk/src/foreign_chain.rs (L42-89)
```rust
    pub fn verify_signature(
        self,
        response: &VerifyForeignTransactionResponse,
        // TODO(#2232): don't use interface API types for public keys
        public_key: &PublicKey,
    ) -> Result<(), VerifyForeignChainError> {
        let expected_payload = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
            request: self.request,
            values: self.expected_extracted_values,
        });

        let expected_payload_hash = expected_payload
            .compute_msg_hash()
            .map_err(|_| VerifyForeignChainError::FailedToComputeMsgHash)?;

        let payload_is_correct = expected_payload_hash == response.payload_hash;

        if !payload_is_correct {
            return Err(VerifyForeignChainError::IncorrectPayloadSigned {
                got: response.payload_hash.clone(),
                expected: expected_payload_hash,
            });
        }
        let verification_result = match (public_key, &response.signature) {
            (
                PublicKey::Secp256k1(secp256k1_public_key),
                SignatureResponse::Secp256k1(k256_signature),
            ) => near_mpc_signature_verifier::verify_ecdsa_signature(
                k256_signature,
                &expected_payload_hash,
                secp256k1_public_key,
            ),
            (PublicKey::Ed25519(ed25519_public_key), SignatureResponse::Ed25519 { signature }) => {
                near_mpc_signature_verifier::verify_eddsa_signature(
                    signature,
                    expected_payload_hash.as_slice(),
                    ed25519_public_key,
                )
            }
            // TODO(#2234): improve types so these errors can't happen
            (PublicKey::Bls12381(_bls12381_g2_public_key), _) => {
                return Err(VerifyForeignChainError::UnexpectedSignatureScheme);
            }
            _ => return Err(VerifyForeignChainError::UnexpectedSignatureScheme),
        };

        verification_result.map_err(|_| VerifyForeignChainError::SignatureVerificationFailed)
    }
```
