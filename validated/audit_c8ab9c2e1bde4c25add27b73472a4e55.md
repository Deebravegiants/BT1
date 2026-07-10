### Title
Caller-Agnostic Queue Key in `verify_foreign_transaction` Enables Queue-Saturation DoS Against Specific Foreign-Tx Verification Requests - (File: crates/contract/src/lib.rs)

---

### Summary

The `VerifyForeignTransactionRequest` struct used as the map key in `pending_verify_foreign_tx_requests` contains no caller identity field. Any unprivileged account can submit 128 identical `verify_foreign_transaction` calls for a known foreign-chain tx ID, saturating the `MAX_PENDING_REQUEST_FAN_OUT = 128` cap and causing every subsequent legitimate submission of the same request to panic with `PendingRequestQueueFull` until the attacker's yields time out. Because the attack can be repeated continuously at negligible cost, a specific bridge transaction can be permanently prevented from receiving an MPC-signed verification response.

---

### Finding Description

**Root cause — caller-agnostic queue key**

`args_into_verify_foreign_tx_request` converts the user-supplied `VerifyForeignTransactionRequestArgs` into a `VerifyForeignTransactionRequest` that contains only `request`, `domain_id`, and `payload_version`:

```rust
// crates/contract/src/dto_mapping.rs  lines 840-848
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

No `predecessor_id` or per-caller discriminator is included. The resulting struct is used verbatim as the `LookupMap` key in `pending_verify_foreign_tx_requests`:

```rust
// crates/contract/src/lib.rs  lines 549-556
let request = args_into_verify_foreign_tx_request(request);
let callback_args = serde_json::to_vec(&(&request,)).unwrap();
self.enqueue_yield_request(
    method_names::RETURN_VERIFY_FOREIGN_TX_AND_CLEAN_STATE_ON_SUCCESS,
    callback_args,
    callback_gas,
    move |this, id| this.add_verify_foreign_tx_request(request, id),
);
```

**Queue cap enforcement**

`push_pending_yield` enforces a hard cap of `MAX_PENDING_REQUEST_FAN_OUT = 128` per key and panics (reverting the call) when exceeded:

```rust
// crates/contract/src/pending_requests.rs  lines 37, 51-58
pub const MAX_PENDING_REQUEST_FAN_OUT: u8 = 128;

if queue.len() >= usize::from(MAX_PENDING_REQUEST_FAN_OUT) {
    env::panic_str(
        &RequestError::PendingRequestQueueFull {
            limit: MAX_PENDING_REQUEST_FAN_OUT,
        }
        .to_string(),
    );
}
```

**Contrast with `sign`**

`SignatureRequest` derives its key from `(predecessor_id, path)` via `derive_tweak`, making the queue per-caller:

```rust
// crates/near-mpc-crypto-types/src/sign.rs  lines 118-125
pub fn new(domain: DomainId, payload: Payload, predecessor_id: &AccountId, path: &str) -> Self {
    let tweak = crate::kdf::derive_tweak(predecessor_id, path);
    SignatureRequest { domain_id: domain, tweak, payload }
}
```

An attacker cannot fill another user's `sign` queue because the key is caller-specific. No such protection exists for `verify_foreign_transaction`.

**Attack path**

1. Attacker observes a target Bitcoin/EVM/Starknet tx ID on the foreign chain (or from the NEAR mempool).
2. Attacker submits 128 `verify_foreign_transaction` calls with the identical `{request, domain_id, payload_version}`, each attaching 1 yoctonear. Cost: 128 yoctonear + gas ≈ negligible.
3. Queue for that key is now full.
4. Legitimate bridge user submits the same request → contract panics with `PendingRequestQueueFull`; user's call is rejected.
5. Attacker's 128 yields eventually time out (NEAR yield-resume timeout, ~200 blocks / ~4 minutes).
6. Attacker immediately re-saturates the queue. Repeat indefinitely.

The test `verify_foreign_transaction__should_queue_duplicates_from_different_callers` explicitly confirms the caller-agnostic design:

```rust
// crates/contract/src/lib.rs  lines 3242-3255
// And: caller bob submits the identical request — a different account would today
// be blocked from receiving a response by alice's submission.
contract.verify_foreign_transaction(request_args);

// Then: both yields are queued under the single (caller-agnostic) request key.
assert_eq!(
    contract.pending_verify_foreign_tx_requests.get(&request).map(|q| q.len()),
    Some(2),
    "duplicate foreign-tx requests from different callers should fan out",
);
```

---

### Impact Explanation

`verify_foreign_transaction` is the on-chain entry point for bridge inbound flows (foreign chain → NEAR). An attacker who knows a target tx ID can permanently prevent MPC nodes from issuing a signed verification response for that transaction. Bridge protocols that rely on this response to release locked funds on NEAR will be unable to complete the transfer. If the bridge enforces a finality deadline on the foreign-chain side, the user's funds may be permanently locked or lost. This is a request-lifecycle invariant break: the contract guarantees that any valid foreign-tx request will eventually be processed, but the attacker can violate that guarantee for any specific tx at negligible cost.

---

### Likelihood Explanation

Foreign-chain tx IDs are public by definition (they appear on the foreign chain and may also appear in the NEAR mempool before inclusion). The attack requires only 128 cheap NEAR transactions (1 yoctonear deposit each) and can be repeated every ~4 minutes to maintain the DoS indefinitely. No privileged access, key material, or threshold collusion is required. Any unprivileged NEAR account can execute this.

---

### Recommendation

Include a per-caller discriminator in the `VerifyForeignTransactionRequest` map key. The simplest approach mirrors `SignatureRequest`: derive a tweak from `(predecessor_id, derivation_path)` and include it in the stored key. This preserves the fan-out design for the same caller submitting duplicates while preventing cross-caller queue saturation. Alternatively, enforce a per-`(caller, request)` submission limit inside `verify_foreign_transaction` before calling `push_pending_yield`.

---

### Proof of Concept

```
// Setup: attacker knows target Bitcoin tx_id = [0xAB; 32]
// Attacker submits 128 identical calls (from any account):
for _ in 0..128 {
    near call mpc-contract.near verify_foreign_transaction \
        '{"request": {"Bitcoin": {"tx_id": "abab...ab", "confirmations": 1, "extractors": ["BlockHash"]}, "domain_id": 0, "payload_version": 1}}' \
        --deposit 0.000000000000000000000001 \
        --gas 300000000000000
}

// Queue is now full (128/128).

// Legitimate bridge user submits the same request:
near call mpc-contract.near verify_foreign_transaction \
    '{"request": {"Bitcoin": {"tx_id": "abab...ab", "confirmations": 1, "extractors": ["BlockHash"]}, "domain_id": 0, "payload_version": 1}}' \
    --deposit 0.000000000000000000000001

// Result: transaction fails with
// "Pending-request queue is full for this request key (limit: 128).
//  Try again once an in-flight response or timeout has cleared room."

// Attacker repeats every ~200 blocks to maintain the DoS.
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

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

**File:** crates/contract/src/lib.rs (L3242-3263)
```rust
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

**File:** crates/near-mpc-crypto-types/src/sign.rs (L117-125)
```rust
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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L124-128)
```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```
