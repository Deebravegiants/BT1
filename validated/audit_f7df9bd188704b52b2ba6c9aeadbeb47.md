### Title
Deleting a multisig member does not purge their stale confirmations on other pending requests, allowing quorum bypass - (File: `multisig/src/lib.rs`, `multisig2/src/lib.rs`)

### Summary
The K-of-N multisig contracts count confirmations stored in the `confirmations: UnorderedMap<RequestId, HashSet<PublicKey>>` (and the analogous `HashSet<String>` in `multisig2`) map to decide when a request has reached quorum. When a member/key is removed via `DeleteKey`/`DeleteMember`, the contract only purges requests that member itself *created*, not the confirmations that member cast on requests created by others. Those stale confirmations remain counted toward the `num_confirmations` threshold even after the confirming key/member has been permanently removed from the account.

### Finding Description
In `multisig/src/lib.rs`, `execute_request()`'s `DeleteKey` branch only removes requests whose *creator* (`signer_pk`) equals the deleted key: [1](#0-0) 

It never touches the `confirmations` set of other pending requests that this key may have already confirmed via `confirm()`. The same limitation exists in `multisig2/src/lib.rs`'s `delete_member()`, which filters requests by `r.member == member` (the request creator), leaving confirmations cast by that member on other members' requests untouched: [2](#0-1) 

The `confirm()` function then evaluates quorum purely by counting entries already present in the `confirmations` HashSet, without checking whether those confirming public keys/members are still valid, current members of the multisig: [3](#0-2) [4](#0-3) 

This mirrors the root cause of the H-1 Hats report: a post-hoc authorization/threshold check (`checkAfterExecution`'s threshold-vs-owner-count comparison, here `confirmations.len()+1 >= num_confirmations`) that is not properly invalidated when the underlying authority set (Safe owners / multisig members) changes mid-flight. In both cases stale/derived state used by the check drifts from the live authorized-signer set, letting the on-chain check pass without genuinely re-validating the current membership of every counted vote.

### Impact Explanation
A member of the multisig can be removed (e.g., due to key rotation, compromise response, or an approved `DeleteKey`/`DeleteMember` request) while they still have a stale, previously-cast confirmation sitting on some other pending request. That removed member's vote continues to count toward quorum indefinitely. As a result, fewer *currently authorized* signers than the configured `num_confirmations` threshold can cause a request (transfer, function call, key/member management, etc.) to execute — effectively bypassing the K-of-N confirmation-bypass guarantee the contract is supposed to enforce. This falls under "Unauthorized execution, confirmation bypass, or state-transition bypass in multisig ... flows that lets an unprivileged user perform actions beyond intended authority," since the remaining live signers execute an action without truly gathering the mandated number of live authorized confirmations.

### Likelihood Explanation
This requires no special privilege beyond being one of the existing (still valid) multisig members who simply confirms a pending request after another member/key has been removed in the interim — a very plausible sequence in normal multisig operation (member rotation is a routine multisig operation, and there is no explicit warning/requirement to first sweep or re-confirm all in-flight requests before/after removing a key). No collusion beyond normal governance flow is required; it only needs timing where a request is left pending across a membership change.

### Recommendation
When executing `DeleteKey` (`multisig/src/lib.rs`) / `DeleteMember` (`multisig2/src/lib.rs`), iterate over **all** pending requests' `confirmations` sets (not just requests created by the removed key/member) and remove the deleted key/member's entry from each, decrementing the effectively counted confirmations. Alternatively, validate at `confirm()`/quorum-check time that every entry in the stored `confirmations` set still corresponds to a currently valid member/key before counting it toward `num_confirmations`.

### Proof of Concept
1. Deploy `multisig` with 3 keys `A, B, C` and `num_confirmations = 2`.
2. `A` calls `add_request(R1)` (e.g., a `Transfer`); `B` calls `confirm(R1)` → `confirmations(R1) = {B}` (1 < 2, not yet executed). [3](#0-2) 
3. Separately, `A` and `C` create+confirm a request `R2` with action `DeleteKey { public_key: B }`, which reaches quorum (2) and executes, deleting `B`'s access key. [1](#0-0) 
4. Because `R1` was created by `A`, not `B`, the `DeleteKey` handler's filter (`r.signer_pk == pk`) does not touch `R1`, so `confirmations(R1)` still contains `B`.
5. `A` now calls `confirm(R1)`. The check `confirmations.len() as u32 + 1 >= self.num_confirmations` evaluates `1 (stale B) + 1 (A) >= 2` → true, and `R1` executes — even though only `A`, a single currently-valid signer, actually authorized it after `B`'s removal. [5](#0-4)

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

**File:** multisig2/src/lib.rs (L292-315)
```rust
    /// Confirm given request with given signing key.
    /// If with this, there has been enough confirmation, a promise with request will be scheduled.
    pub fn confirm(&mut self, request_id: RequestId) -> PromiseOrValue<bool> {
        self.assert_valid_request(request_id);
        let member = self
            .current_member()
            .unwrap_or_else(|| env::panic_str("Must be validated above"));
        let mut confirmations = self.confirmations.get(&request_id).unwrap();
        assert(
            !confirmations.contains(&member.to_string()),
            "Already confirmed this request with this key",
        );
        if confirmations.len() as u32 + 1 >= self.num_confirmations {
            let request = self.remove_request(request_id);
            /********************************
            NOTE: If the tx execution fails for any reason, the request and confirmations are removed already, so the client has to start all over
            ********************************/
            self.execute_request(request)
        } else {
            confirmations.insert(member.to_string());
            self.confirmations.insert(&request_id, &confirmations);
            PromiseOrValue::Value(true)
        }
    }
```

**File:** multisig2/src/lib.rs (L355-379)
```rust
    /// Delete member from the list. Removes access key if the member is key based.
    fn delete_member(&mut self, promise: Promise, member: MultisigMember) -> Promise {
        assert(
            self.members.len() - 1 >= self.num_confirmations as u64,
            "Removing given member will make total number of members below number of confirmations",
        );
        // delete outstanding requests by public_key
        let request_ids: Vec<u32> = self
            .requests
            .iter()
            .filter_map(|(k, r)| if r.member == member { Some(k) } else { None })
            .collect();
        for request_id in request_ids {
            // remove confirmations for this request
            self.confirmations.remove(&request_id);
            self.requests.remove(&request_id);
        }
        // remove num_requests_pk entry for member
        self.num_requests_pk.remove(&member.to_string());
        self.members.remove(&member);
        match member {
            MultisigMember::AccessKey { public_key } => promise.delete_key(public_key.into()),
            MultisigMember::Account { account_id: _ } => promise,
        }
    }
```
