### Title
Caller-Agnostic `verify_foreign_transaction` Queue Key Allows Any Unprivileged Account to Saturate the Fan-Out Queue and Block Legitimate Bridge Verifications - (File: crates/contract/src/lib.rs)

### Summary
The `verify_foreign_transaction()` endpoint stores pending requests under a key (`VerifyForeignTransactionRequest`) that does **not** include the caller's identity. Any unprivileged account can submit the same foreign-chain transaction verification request and occupy slots in the bounded fan-out queue. Because the queue cap is 128 and the minimum deposit is 1 yoctoNEAR, a single attacker account can saturate the queue for any specific foreign transaction at negligible cost, preventing legitimate bridge services from enqueuing their own verification requests until the queue drains.

### Finding Description
The `sign()` function derives a per-caller `SignatureRequest` key by hashing `(predecessor_id, path)` into a `Tweak`, so each caller's request occupies a distinct map entry and cannot be interfered with by other callers. [1](#0-0) 

The `verify_foreign_transaction()` function, by contrast, converts the caller's arguments into a `VerifyForeignTransactionRequest` that contains only `(domain_id, payload_version, ForeignChainRpcRequest)` — no caller identity, no tweak. [2](#0-1) 

The stored key type confirms the absence of any caller-binding field: [3](#0-2) 

The contract's own unit test explicitly labels this behaviour "caller-agnostic": [4](#0-3) 

The fan-out queue is capped at `MAX_PENDING_REQUEST_FAN_OUT = 128`. Once the cap is reached, `push_pending_yield` panics with `PendingRequestQueueFull`, rejecting any further submissions for that request key: [5](#0-4) 

Because the queue key does not bind to the caller, a single attacker account can submit 128 `verify_foreign_transaction` calls for the same foreign-chain transaction (each call creates a distinct NEAR yield data-id, so all 128 are accepted). After that, any legitimate bridge service attempting to submit the same request receives `PendingRequestQueueFull` and is blocked until the queue drains — either via an MPC response (which drains all 128 slots at once, but the bridge service was never in the queue and receives nothing) or via 128 sequential timeouts. [6](#0-5) 

### Impact Explanation
A bridge service that relies on `verify_foreign_transaction` to release funds on NEAR after observing a foreign-chain event can be blocked from submitting its verification request for any specific transaction. If the bridge operates under a time-sensitive challenge window (e.g., an optimistic bridge where unchallenged claims expire), the attacker can hold the queue saturated for the duration of that window, causing the bridge to miss its deadline and permanently freeze the associated funds in the verified foreign-chain flow. Even without a hard deadline, the attacker can continuously re-saturate the queue as it drains, indefinitely delaying fund releases. This maps to the allowed Medium impact: "request-lifecycle manipulation that breaks production safety/accounting invariants."

### Likelihood Explanation
The attack is trivially cheap: 128 calls × 1 yoctoNEAR deposit = effectively zero cost. A single NEAR account is sufficient; no special privileges, no threshold collusion, and no TEE access are required. The attacker only needs to know the target foreign-chain transaction ID (publicly observable on the foreign chain). The attack can be scripted to re-saturate the queue automatically as timeouts clear slots.

### Recommendation
Bind the `VerifyForeignTransactionRequest` map key to the caller's identity, mirroring the `sign()` design. Introduce a per-caller derivation (e.g., a tweak from `(predecessor_id, derivation_path)`) so that each caller's request occupies a distinct map entry and cannot be displaced or saturated by other accounts. Alternatively, enforce a meaningful per-call deposit (not 1 yoctoNEAR) to raise the economic cost of queue saturation to a level that deters sustained attacks.

### Proof of Concept
1. Alice (bridge service) observes Bitcoin tx `X` confirmed on-chain and prepares to call `verify_foreign_transaction({ domain_id: 0, payload_version: V1, request: Bitcoin({ tx_id: X, confirmations: 6, extractors: [BlockHash] }) })`.
2. Mallory, observing the same mempool or block, submits the identical `verify_foreign_transaction` call 128 times from a single account (each call attaches 1 yoctoNEAR). All 128 are accepted and queued under the same caller-agnostic key.
3. Alice submits her call. The contract panics with `PendingRequestQueueFull { limit: 128 }`. Alice's transaction fails and she receives no yield.
4. MPC nodes process the request and call `respond_verify_foreign_tx`. All 128 of Mallory's yields are drained; Alice's yield was never enqueued, so Alice receives no response.
5. Mallory immediately re-submits 128 calls. Alice's next attempt again fails with `PendingRequestQueueFull`.
6. If Alice's bridge has a challenge window of N blocks, Mallory sustains the attack for N blocks at a total cost of at most `128 × ceil(N / timeout_blocks)` yoctoNEAR — negligible — while Alice's bridge operation is permanently blocked for that transaction. [2](#0-1) [7](#0-6) [8](#0-7)

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

**File:** crates/contract/tests/snapshots/abi__abi_has_not_changed.snap (L5135-5155)
```text
        "VerifyForeignTransactionRequest": {
          "type": "object",
          "required": [
            "domain_id",
            "payload_version",
            "request"
          ],
          "properties": {
            "domain_id": {
              "$ref": "#/definitions/DomainId"
            },
            "payload_version": {
              "type": "integer",
              "format": "uint8",
              "minimum": 0.0
            },
            "request": {
              "$ref": "#/definitions/ForeignChainRpcRequest"
            }
          }
        },
```

**File:** crates/contract/src/pending_requests.rs (L24-59)
```rust
/// Maximum number of concurrent yield-resume promises that can be queued for a single
/// request key (i.e. the number of duplicate submissions whose responses fan out from
/// one MPC reply).
///
/// The ceiling is needed because `respond*` drains the entire queue in one call: every
/// queued yield triggers a host-side `promise_yield_resume`, paid for out of the
/// responder's 300 TGas budget. Without a cap, an attacker could enqueue enough
/// duplicates to make `respond*` run out of gas and strand every queued caller.
///
/// 128 is validated empirically by the sandbox test
/// `test_contract_request_duplicate_requests_fan_out`, which fills the queue to this
/// cap across all four signature schemes and confirms `respond*` drains it inside its
/// 300 TGas budget.
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

**File:** crates/contract/src/pending_requests.rs (L90-112)
```rust
/// Account for one timed-out yield against `request`: pop the oldest queued yield
/// from the fan-out for `request`. A no-op if the request is absent (e.g. `respond*`
/// already drained it) or the stored queue had no entries to pop.
///
/// Yields are removed in FIFO order because they were appended in submission order
/// and time out in that same order — so the timing-out yield is always the head.
/// If the queue empties (or was already empty), the map entry itself is removed.
pub(crate) fn pop_oldest_pending_yield<K>(requests: &mut LookupMap<K, Vec<YieldIndex>>, request: &K)
where
    K: BorshSerialize + BorshDeserialize + Clone + Ord,
{
    let Some(queue) = requests.get_mut(request) else {
        return;
    };
    if queue.is_empty() {
        requests.remove(request);
        return;
    }
    queue.remove(0);
    if queue.is_empty() {
        requests.remove(request);
    }
}
```
