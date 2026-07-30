## Title
Stale confirmations from revoked keys count toward the multisig threshold, allowing execution with fewer than `num_confirmations` live keys - (`multisig/src/lib.rs`)

### Summary
`DeleteKey` only purges requests and confirmation sets for requests *originated* by the deleted public key. It never scans the confirmation sets of *other* requests for membership of the deleted key. `confirm()` then determines whether a request is ready to execute purely by `HashSet::len()`, with no check that any of the stored public keys are still valid access keys on the account. As a result, a confirmation cast by a key that is later deleted remains permanently counted toward the threshold, letting a request execute with fewer live/authorized confirmations than `num_confirmations` requires.

### Finding Description
When a request is confirmed, the signer's `PublicKey` is stored in a `HashSet<PublicKey>` keyed by `request_id`: [1](#0-0) 

When `DeleteKey` is executed, the cleanup logic only removes requests (and their confirmation sets) that were *originated* by the deleted key — it filters on `r.signer_pk == pk`, i.e. the request creator, not on membership inside other requests' `confirmations` sets: [2](#0-1) 

So if key `pk_B` confirmed a request `R` that was *created by a different key* (`pk_A`), and `pk_B` is later removed from the account via an unrelated `DeleteKey{pk_B}` request, `R`'s confirmation set still contains `pk_B`. Nothing in the codebase ever revisits or invalidates that entry.

`get_confirmations` simply returns the raw contents of that stale set, so it will keep reporting the revoked key as an active confirmer indefinitely: [3](#0-2) 

Finally, `confirm()`'s threshold check is purely numeric — `confirmations.len() as u32 + 1 >= self.num_confirmations` — with no validation that the keys inside `confirmations` (or the calling key) are still live access keys on the account: [4](#0-3) 

Note that `confirm()`/`add_request()` do enforce `predecessor_account_id() == current_account_id()`, so the *caller itself* must be a currently-valid access key (the runtime verifies key/nonce before a transaction executes as the account). But the check never re-validates the *previously stored* confirmations already sitting in the `HashSet`. That means old confirmations survive key rotation/revocation and continue to count toward the threshold.

### Impact Explanation
This breaks the core multisig invariant: "a request executes only once `num_confirmations` *currently authorized* keys have approved it." A request can execute with only `num_confirmations - 1` (or fewer) genuinely live keyholders agreeing, because one or more slots in the threshold are filled by ghost confirmations from keys that have since been revoked (e.g., a compromised key that was proactively removed, or a departing signer). This is a confirmation-bypass / unauthorized-execution flaw in the multisig request lifecycle, directly impacting fund-moving actions (`Transfer`, `FunctionCall`, `AddKey`, etc.) approved through `confirm()`.

### Likelihood Explanation
This requires no attacker privilege beyond being one of the legitimate signers who eventually gets removed, or simply the natural, expected operational flow of a wallet rotating/revoking a key after it had already confirmed an in-flight, not-yet-executed request. Key rotation is a normal administrative action in these wallets, and pending unconfirmed requests are common (the contract even bounds them via `active_requests_limit`/`REQUEST_COOLDOWN`), so the precondition (a pending request confirmed by a key that is later deleted) is realistic and easy to trigger.

### Recommendation
When executing `DeleteKey`, iterate over all entries in `self.confirmations` (not just requests originated by the deleted key) and remove the deleted key from every confirmation set, e.g. `self.confirmations.get(&id)` → `set.remove(&pk)` → re-insert. Additionally, `confirm()`/threshold evaluation should re-validate that all keys in a confirmation set are still valid access keys before counting them (or simply purge them defensively at confirm-time), rather than trusting historical `HashSet` membership.

### Proof of Concept
1. Deploy multisig with `num_confirmations = 2` and three access keys: `pk_A`, `pk_B`, `pk_C`.
2. `pk_A` calls `add_request(R)` for a `Transfer` action (not `add_request_and_confirm`), so `R`'s confirmation set starts empty.
3. `pk_B` calls `confirm(R)` → confirmation set becomes `{pk_B}` (1 < 2, not yet executed) — see `multisig/src/lib.rs:248-266`.
4. A separate request `D = DeleteKey{public_key: pk_B}` is created and confirmed to completion by `pk_A` and `pk_C` (2-of-3), executing and removing `pk_B` from the account's access keys — see `multisig/src/lib.rs:198-216`. Note `D`'s cleanup only scans `self.requests` for `r.signer_pk == pk_B` (none, since `pk_B` didn't originate any request), so `R`'s confirmation set `{pk_B}` is left untouched.
5. `get_confirmations(R)` still returns `[pk_B]`, even though `pk_B` is no longer a valid key on the account — see `multisig/src/lib.rs:339-346`.
6. `pk_C` calls `confirm(R)`. Inside `confirm()`, `confirmations.len() (1) + 1 == 2 >= num_confirmations (2)`, so `execute_request` runs the `Transfer` — see `multisig/src/lib.rs:255-260`. The transfer executes despite only one currently-valid key (`pk_C`) ever having actually confirmed it live; `pk_A` (the creator) never confirmed, and `pk_B`'s confirmation is from a revoked key.

This demonstrates a request executing under a 2-of-3 policy with effectively only 1 live confirming key, violating the multisig threshold guarantee.

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

**File:** multisig/src/lib.rs (L339-346)
```rust
    pub fn get_confirmations(&self, request_id: RequestId) -> Vec<Base58PublicKey> {
        self.confirmations
            .get(&request_id)
            .expect("No such request")
            .into_iter()
            .map(|key| Base58PublicKey::try_from(key).expect("Failed to covert key to base58"))
            .collect()
    }
```
