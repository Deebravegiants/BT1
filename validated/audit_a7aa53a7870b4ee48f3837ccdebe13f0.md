### Title
Caller-Agnostic `verify_foreign_transaction` Fan-Out Queue Exhaustion Enables Per-Transaction DoS - (File: crates/contract/src/pending_requests.rs)

### Summary

The `verify_foreign_transaction` endpoint uses a caller-agnostic request key (`VerifyForeignTransactionRequest` contains no `predecessor_id`), while the fan-out queue for each key is hard-capped at `MAX_PENDING_REQUEST_FAN_OUT = 128`. A single unprivileged attacker can submit 128 identical verification requests for a specific foreign transaction, filling the queue to its cap and causing every subsequent legitimate caller's request for that same transaction to be rejected with `PendingRequestQueueFull`. This is structurally analogous to the Axelar flow-limit exhaustion: a shared, bounded resource is consumed entirely by one actor, blocking all others.

### Finding Description

The `sign` and `request_app_private_key` endpoints both embed the caller's identity into the request key via a tweak derived from `predecessor_id` and `path`:

```rust
// crates/contract/src/lib.rs ~L379-384
let request = SignatureRequest::new(
    request.domain_id,
    request.payload,
    &predecessor,   // caller identity baked into the key
    &request.path,
);
```

`SignatureRequest` therefore has a unique key per `(caller, domain, path, payload)` tuple. [1](#0-0) 

By contrast, `verify_foreign_transaction` discards the predecessor after the deposit check and constructs a key that contains only `(request, domain_id, payload_version)`:

```rust
// crates/contract/src/lib.rs ~L526-556
self.check_request_preconditions(...);   // predecessor returned but never used in key
let request = args_into_verify_foreign_tx_request(request);  // no predecessor_id
self.enqueue_yield_request(..., move |this, id| this.add_verify_foreign_tx_request(request, id));
``` [2](#0-1) 

The resulting `VerifyForeignTransactionRequest` type has no caller field:

```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
``` [3](#0-2) 

All callers submitting the same `(chain_request, domain_id, payload_version)` tuple share one fan-out queue entry. The queue is capped at `MAX_PENDING_REQUEST_FAN_OUT = 128` to prevent gas exhaustion in `respond*`:

```rust
pub const MAX_PENDING_REQUEST_FAN_OUT: u8 = 128;

pub(crate) fn push_pending_yield<K>(...) {
    let queue = requests.entry(request).or_default();
    if queue.len() >= usize::from(MAX_PENDING_REQUEST_FAN_OUT) {
        env::panic_str(&RequestError::PendingRequestQueueFull { limit: MAX_PENDING_REQUEST_FAN_OUT }.to_string());
    }
    queue.push(YieldIndex { data_id });
}
``` [4](#0-3) 

An attacker who submits 128 calls to `verify_foreign_transaction` with the same `(tx_id, domain_id, payload_version)` fills the queue to its cap. Every subsequent legitimate caller targeting that same foreign transaction receives `PendingRequestQueueFull` and is rejected. The attacker's cost is 128 × 1 yoctonear + gas — negligible on NEAR. The queue only drains when MPC nodes respond (or after `REQUEST_EXPIRATION_BLOCKS = 200` blocks), at which point the attacker can immediately refill it.

The test suite itself acknowledges the caller-agnostic nature of the key:

```rust
// And: caller bob submits the identical request — a different account would today
// be blocked from receiving a response by alice's submission.
``` [5](#0-4) 

### Impact Explanation

`verify_foreign_transaction` is the primary mechanism for bridge inbound flows (e.g., Omnibridge: foreign chain → NEAR). A targeted attacker who knows a specific bridge deposit transaction ID can front-run the bridge relayer or the depositor, fill the 128-slot queue for that `tx_id`, and prevent the legitimate verification from being queued. The depositor's funds remain locked until the queue drains and they successfully retry. The attacker can sustain the block across multiple drain cycles at negligible cost. This breaks the request-lifecycle safety invariant for bridge operations without requiring any privileged access or operator misconfiguration.

This matches the allowed Medium impact: *"request-lifecycle manipulation that breaks production safety/accounting invariants."*

### Likelihood Explanation

The attack requires only:
1. Knowledge of the target foreign transaction ID (publicly observable on the foreign chain).
2. The ability to call `verify_foreign_transaction` 128 times with 1 yoctonear each — no special role, no threshold collusion.

On NEAR, 128 transactions can be submitted in a single block via batching or parallel submission. The attacker can monitor the mempool or the foreign chain for incoming bridge deposits and front-run the relayer. The cost is effectively zero.

### Recommendation

Include the caller's `predecessor_id` in the `VerifyForeignTransactionRequest` key, mirroring the approach used by `sign` and `request_app_private_key`. This gives each caller an independent queue slot, preventing one account from exhausting the shared cap for a given foreign transaction.

Concretely, add a `tweak` or `caller` field to `VerifyForeignTransactionRequest` derived from `predecessor_id` (and optionally a derivation path), so the map key is `(caller, domain_id, payload_version, chain_request)` rather than `(domain_id, payload_version, chain_request)`. The fan-out design (multiple callers sharing one MPC computation) can be preserved by deduplicating at the node level rather than at the contract storage key level, or by accepting that each caller gets an independent queue entry and independent MPC computation.

### Proof of Concept

1. A bridge relayer is about to call `verify_foreign_transaction` for Bitcoin tx `0xDEAD...` on domain 0.
2. Attacker observes the pending Bitcoin transaction on-chain.
3. Attacker submits 128 calls to `verify_foreign_transaction` with `{ request: Bitcoin(tx_id=0xDEAD...), domain_id: 0, payload_version: V1 }`, each with 1 yoctonear deposit.
4. The fan-out queue for that request key is now at capacity (128/128). [6](#0-5) 
5. The bridge relayer's call to `verify_foreign_transaction` with the same arguments panics with `PendingRequestQueueFull`. [7](#0-6) 
6. MPC nodes process the attacker's 128 requests and call `respond_verify_foreign_tx`, draining the queue. [8](#0-7) 
7. Attacker immediately resubmits 128 calls, refilling the queue before the relayer can retry.
8. The bridge deposit remains unverified and the depositor's funds remain locked for as long as the attacker sustains the attack.

### Citations

**File:** crates/near-mpc-crypto-types/src/sign.rs (L111-125)
```rust
pub struct SignatureRequest {
    pub tweak: Tweak,
    pub payload: Payload,
    pub domain_id: DomainId,
}

impl SignatureRequest {
    pub fn new(domain: DomainId, payload: Payload, predecessor_id: &AccountId, path: &str) -> Self {
        let tweak = crate::kdf::derive_tweak(predecessor_id, path);
        SignatureRequest {
            domain_id: domain,
            tweak,
            payload,
        }
    }
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

**File:** crates/contract/src/lib.rs (L691-754)
```rust
    #[handle_result]
    pub fn respond_verify_foreign_tx(
        &mut self,
        request: VerifyForeignTransactionRequest,
        response: VerifyForeignTransactionResponse,
    ) -> Result<(), Error> {
        let signer = Self::assert_caller_is_signer();

        log!(
            "respond_verify_foreign_tx: signer={}, request={:?}",
            &signer,
            &request
        );

        self.assert_caller_is_attested_participant_and_protocol_active();

        if !self.protocol_state.is_running_or_resharing() {
            return Err(InvalidState::ProtocolStateNotRunning.into());
        }

        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }

        let domain = request.domain_id;
        let public_key = self.public_key_extended(domain.0.into())?;

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
            }
            (signature_response, public_key_requested) => {
                return Err(RespondError::SignatureSchemeMismatch {
                    mpc_scheme: Box::new(signature_response.clone()),
                    user_scheme: Box::new(public_key_requested),
                }
                .into());
            }
        };

        if !signature_is_valid {
            return Err(RespondError::InvalidSignature.into());
        }

        pending_requests::resolve_yields_for(
            &mut self.pending_verify_foreign_tx_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
    }
```

**File:** crates/contract/src/lib.rs (L3242-3244)
```rust
        // And: caller bob submits the identical request — a different account would today
        // be blocked from receiving a response by alice's submission.
        let bob = AccountId::from_str("bob.near").unwrap();
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L124-128)
```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```

**File:** crates/contract/src/pending_requests.rs (L37-59)
```rust
pub const MAX_PENDING_REQUEST_FAN_OUT: u8 = 128;

/// Append a yield index to the pending-request fan-out queue for `request`.
///
/// Panics with `RequestError::PendingRequestQueueFull` if the resulting queue would
/// exceed `MAX_PENDING_REQUEST_FAN_OUT`.
pub(crate) fn push_pending_yield<K>(
    requests: &mut LookupMap<K, Vec<YieldIndex>>,
    request: K,
    data_id: CryptoHash,
) where
    K: BorshSerialize + BorshDeserialize + Clone + Ord,
{
    let queue = requests.entry(request).or_default();
    if queue.len() >= usize::from(MAX_PENDING_REQUEST_FAN_OUT) {
        env::panic_str(
            &RequestError::PendingRequestQueueFull {
                limit: MAX_PENDING_REQUEST_FAN_OUT,
            }
            .to_string(),
        );
    }
    queue.push(YieldIndex { data_id });
```

**File:** crates/contract/src/errors.rs (L37-41)
```rust
    #[error(
        "Pending-request queue is full for this request key (limit: {limit}). Try again once an in-flight response or timeout has cleared room."
    )]
    PendingRequestQueueFull { limit: u8 },
}
```
