## Finding: Stale confirmations from removed multisig keys are not purged, allowing a revoked key to still count toward execution threshold

### Title
Removed multisig key's prior confirmations remain valid and still count toward execution threshold - (File: `multisig/src/lib.rs`)

### Summary
The root cause pattern in the referenced GaugeController report is that removal of an entity (a gauge) does not clean up the per-user state that referenced it, so stale state keeps affecting accounting after removal. `multisig/src/lib.rs` has the same class of bug: when a multisig key is removed via `MultiSigRequestAction::DeleteKey`, the contract only purges requests that the removed key itself *created*, but never scans the `confirmations` map to strip that key's confirmations from other pending requests it had only *confirmed*. Those stale confirmations continue to count toward `num_confirmations` after the key is deleted.

### Finding Description
`execute_request`'s `DeleteKey` branch is the only cleanup logic that runs when a key is removed: [1](#0-0) 

It filters `self.requests` for entries where `r.signer_pk == pk` (i.e., requests *created* by the deleted key) and removes those requests plus their confirmation sets. It does not touch `self.confirmations` entries for other, still-pending requests where the deleted key merely added a confirmation via `confirm()`: [2](#0-1) 

Confirmations are stored in a `HashSet<PublicKey>` per request, independent from key validity: `confirmations.insert(env::signer_account_pk())`. Since the contract never re-validates that a `PublicKey` in a confirmation set still exists as an access key on the account, a confirmation added before a key was deleted is still counted when tallying `confirmations.len() as u32 + 1 >= self.num_confirmations` for that request.

### Impact Explanation
This is exactly the scenario the multisig pattern is meant to prevent: revoking a compromised or offboarded signer's key (via `DeleteKey`) is supposed to eliminate that signer's influence going forward. Instead, any request the revoked key confirmed *before* removal keeps its confirmation "vote," lowering the effective number of live signers required to reach `num_confirmations`. E.g., in a 3-of-5 multisig, if a compromised key B confirmed a pending Transfer request before being revoked, the request only needs one more confirmation from a remaining live key to execute — effectively a 2-of-4 threshold bypass using a revoked signer's stale approval. This maps to the High-impact category of "confirmation bypass ... in multisig ... flows that lets an unprivileged user perform actions beyond intended authority," since the deleted key's holder (now fully unprivileged, having lost their key) still exerts binding authority over fund-moving actions.

### Likelihood Explanation
This is realistically triggered any time governance rotates/revokes a signer (the documented and expected key-management flow) while there is a pending, partially-confirmed request in-flight. No malicious collusion beyond the normal act of revoking a key is required; it is a state-cleanup gap in code that already runs on every `DeleteKey` action.

### Recommendation
When executing `DeleteKey`, also scan `self.confirmations` for all requests and remove the deleted `pk` from every confirmation `HashSet`, not just from requests it created. Alternatively, validate confirmation set membership against currently active keys at confirm-execution time before counting them toward `num_confirmations`.

### Proof of Concept
1. Deploy `MultiSigContract::new(3)` with 5 keys A, B, C, D, E.
2. Key A calls `add_request` for a `Transfer` action → request R (id 0).
3. Key B calls `confirm(0)` → confirmations = {B}, count 1 (below 3, pending).
4. Governance detects key B is compromised; keys A, C, D approve a `DeleteKey{public_key: B}` request, which executes and calls `promise.delete_key(B)`. Per `execute_request`'s `DeleteKey` branch, since B never created any request, no entries are removed from `self.confirmations` for request 0 — B's confirmation on request 0 remains.
5. Key C calls `confirm(0)` → confirmations = {B(stale), C}, count 2 (still below 3).
6. Key D calls `confirm(0)` → confirmations = {B(stale), C, D}, count 3 ≥ `num_confirmations` → `execute_request` runs, transferring funds, even though B's access key was already deleted and B should have zero remaining influence. [1](#0-0) [2](#0-1)

### Citations

**File:** multisig/src/lib.rs (L198-216)
```rust
                MultiSigRequestAction::DeleteKey { public_key } => {
                    self.assert_self_request(receiver_id.clone());
                    let pk: PublicKey = public_key.into();
                    // delete outstanding requests by public_key
                    let request_ids: Vec<u32> = self
                        .requests
                        .iter()
                        .filter(|(_k, r)| r.signer_pk == pk)
                        .map(|(k, _r)| k)
                        .collect();
                    for request_id in request_ids {
                        // remove confirmations for this request
                        self.confirmations.remove(&request_id);
                        self.requests.remove(&request_id);
                    }
                    // remove num_requests_pk entry for public_key
                    self.num_requests_pk.remove(&pk);
                    promise.delete_key(pk)
                }
```

**File:** multisig/src/lib.rs (L246-266)
```rust
    /// Confirm given request with given signing key.
    /// If with this, there has been enough confirmation, a promise with request will be scheduled.
    pub fn confirm(&mut self, request_id: RequestId) -> PromiseOrValue<bool> {
        self.assert_valid_request(request_id);
        let mut confirmations = self.confirmations.get(&request_id).unwrap();
        assert!(
            !confirmations.contains(&env::signer_account_pk()),
            "Already confirmed this request with this key"
        );
        if confirmations.len() as u32 + 1 >= self.num_confirmations {
            let request = self.remove_request(request_id);
            /********************************
            NOTE: If the tx execution fails for any reason, the request and confirmations are removed already, so the client has to start all over
            ********************************/
            self.execute_request(request)
        } else {
            confirmations.insert(env::signer_account_pk());
            self.confirmations.insert(&request_id, &confirmations);
            PromiseOrValue::Value(true)
        }
    }
```
