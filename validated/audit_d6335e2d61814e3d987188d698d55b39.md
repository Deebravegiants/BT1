## Finding confirmed

The vulnerability is real and located in `multisig/src/lib.rs` in the `DeleteKey` handling inside `execute_request` and the confirmation counting in `confirm`.

### Title
Stale confirmations from a deleted multisig key still count toward the execution threshold - (multisig/src/lib.rs)

### Summary
When a public key is removed via a `DeleteKey` multisig request, the contract only purges pending *requests authored by* that key. It never scrubs that key from the `confirmations` set of *other* requests it had merely confirmed. Because `confirm()` counts confirmations purely by set size/membership with no revalidation against currently-authorized keys, a since-deleted key's earlier confirmation still counts toward `num_confirmations` at execution time.

### Finding Description
`confirm()` checks the confirmation count and, once the threshold is met, calls `execute_request`: [1](#0-0) 

The `DeleteKey` action, executed inside `execute_request`, only cleans up requests whose `signer_pk` (the request *creator*) equals the deleted key, and clears `num_requests_pk` for that key: [2](#0-1) 

It never iterates `self.confirmations` to remove the deleted `pk` from confirmation sets of other, still-pending requests that this key had confirmed but not authored. Consequently, `self.confirmations` (`UnorderedMap<RequestId, HashSet<PublicKey>>`) can retain an entry from a key that no longer has on-chain access key privileges.

Since threshold evaluation in `confirm()` is purely `confirmations.len() as u32 + 1 >= self.num_confirmations` — a raw count of the `HashSet<PublicKey>` — with no re-validation that every key in that set is a currently authorized full-access key of the account, a stale confirmation is indistinguishable from a live one and is counted at execute time.

### Impact Explanation
This allows a fund-moving (or otherwise dangerous, e.g. `AddKey`/`FunctionCall`) request to reach the execution threshold and fire using a vote from a key that is no longer authorized to sign for the account, effectively bypassing the intended "current signer set" authorization invariant. This falls under "Unauthorized execution, confirmation bypass ... in multisig ... flows" and can also lead to unauthorized transfer of NEAR funds if the stale vote is the deciding one.

### Likelihood Explanation
Requires two independent, but entirely ordinary, actions that already happen in normal multisig lifecycle: (1) a key confirms some pending request without being its author, and (2) that same key is later removed via a separate `DeleteKey` request while the first request is still pending. No privileged access beyond normal multisig participation is required to trigger the stale-vote condition to persist; the bug is in the DeleteKey cleanup logic itself, not attacker-authored malicious input.

### Recommendation
When executing `DeleteKey`, iterate all entries in `self.confirmations` (not only requests authored by the deleted key) and remove the deleted public key from every confirmation `HashSet`. Alternatively/additionally, revalidate at `confirm()`/execution time that all keys present in a request's confirmation set are still valid access keys before counting them toward `num_confirmations`.

### Proof of Concept
1. Key `K1` creates a `Transfer` request `R` (`add_request`), `num_confirmations = 3`.
2. Key `K2` calls `confirm(R)` — adds `K2` to `confirmations[R]` (count = 1, below threshold).
3. Separately, `K1`/other signers create and confirm a `DeleteKey { public_key: K2 }` request to threshold, which executes: this only removes requests where `signer_pk == K2` (none, since `K2` didn't author `R`), and calls `promise.delete_key(K2)` removing `K2`'s on-chain access key. `confirmations[R]` still contains `K2`.
4. `K3` and `K4` (or fewer keys, depending on threshold) call `confirm(R)`. The count check `confirmations.len() + 1 >= num_confirmations` includes the stale `K2` entry, so the request executes with fewer *currently valid* signer confirmations than `num_confirmations` actually requires — i.e., `K2`'s vote (from a now-nonexistent key) was necessary to reach threshold and reach `execute_request`.

A unit test analogous to `add_key_delete_key_storage_cleared` in `multisig/src/lib.rs` (lines 575-631) but where the deleted key is a *confirmer* of a separate pending transfer request (not its author) demonstrates that `confirmations.get(&request_id)` still contains the deleted key's entry after the `DeleteKey` request executes, and that a subsequent `confirm()` call from a legitimate key triggers execution using that stale vote. [2](#0-1) [1](#0-0)

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
