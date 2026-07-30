## Finding

The vulnerability described is real and present in the current code.

### Title
Stale confirmations from revoked multisig keys can satisfy quorum after `DeleteKey` execution - (`multisig/src/lib.rs`)

### Summary
`confirm()` counts confirmations purely by set size/membership, and `DeleteKey` execution only purges *requests* whose `signer_pk` matches the deleted key — it never scrubs the deleted key's public key out of the `confirmations` HashSet of *other* pending requests. This lets a request reach quorum using a confirmation entry belonging to a key that has since been revoked.

### Finding Description
`confirm()` reads the existing `confirmations` set for a request and simply checks its size against `num_confirmations`, with no re-validation that each pk in the set is still a currently authorized key on the account: [1](#0-0) 

When a `DeleteKey` action executes, the cleanup logic only removes *requests originally added by* the deleted key (`r.signer_pk == pk`), and clears `num_requests_pk` for that key. It does **not** scan `self.confirmations` to strip that key's pk from confirmation sets of other still-pending requests: [2](#0-1) 

So the sequence:
1. K1 (2-of-3 multisig) calls `add_request(R)` — creates `R` with empty confirmation set.
2. K2 calls `confirm(R)` — since `1 < 2`, K2's pk is inserted into `R`'s confirmations set (not yet executed).
3. A separate request `DeleteKey(K2)` reaches quorum and executes, revoking K2's access key on-chain, but leaves `confirmations[R] = {K2}` untouched because the cleanup loop only filters on `r.signer_pk`.
4. K3 calls `confirm(R)` — `confirmations.len() (1) + 1 >= 2`, so quorum is satisfied and `execute_request(R)` runs, even though only K3 is a currently valid signer contributing a fresh confirmation; K2's contribution is stale.

The intended invariant of a k-of-n multisig is that k *currently authorized* keys must approve at the moment of execution. This code instead treats any historically recorded confirmation as still valid indefinitely, even after the underlying key has been deprovisioned by the multisig's own governance action.

### Impact Explanation
This degrades the effective threshold after any key rotation/removal: a 2-of-3 multisig with one pending confirmation from a soon-to-be-removed key silently becomes 1-of-2 for the remaining signers on that specific request, without any of the remaining current signers being aware their approval alone (combined with a stale record) is sufficient. This weakens the core security guarantee of the multisig — a genuine confirmation-bypass in the request execution flow, matching the High-severity category "confirmation bypass ... in multisig ... flows."

### Likelihood Explanation
This is deterministically reachable with normal contract usage (no external unauthorized attacker needed): any 2-of-3+ multisig that ever revokes a key while that key has outstanding confirmations on other unexecuted requests hits this path. Key rotation/removal is a normal, expected multisig operation, making this a realistic and easily triggered scenario rather than a contrived edge case.

### Recommendation
When executing `DeleteKey`, iterate `self.confirmations` (not just `self.requests`) and remove the deleted pk from every confirmation set, not only from requests it originally signed. Alternatively/additionally, `confirm()` could validate each entry in the request's confirmation set against the account's current full access keys before counting them toward quorum, ensuring only live keys are counted.

### Proof of Concept
1. Deploy `MultiSigContract::new(2)` with keys K1, K2, K3.
2. As K1, `add_request(R)` for e.g. a `Transfer`.
3. As K2, `confirm(R)` → confirmations for `R` = `{K2}`, request still pending (1 < 2).
4. As K1 (or via existing quorum), submit and confirm a separate request `DeleteKey{public_key: K2}` targeting the multisig's own account until it executes — this removes K2's access key and purges requests where `signer_pk == K2`, but `confirmations[R]` still equals `{K2}` (verify via `get_confirmations(R)`).
5. As K3, call `confirm(R)` → `confirmations.len() (1) + 1 >= 2` is true, so `execute_request(R)` fires and the transfer executes, despite K2 no longer being an authorized key. [3](#0-2)

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

**File:** multisig/src/lib.rs (L248-266)
```rust
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
