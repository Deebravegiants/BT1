## Analysis

The reported class is a **stale-vote / accounting failure**: a voter's confirmation continues to count toward a quorum/threshold even after the voter is removed from the voting body, letting the removal itself help satisfy a threshold that should require live, current signers.

This exact pattern exists in the `multisig2` contract's member-removal path.

### Root cause

`delete_member()` in `multisig2/src/lib.rs` only purges **requests that the removed member originated** (`r.member == member`). It never scans the `confirmations` map to strip the removed member's confirmation from *other* still-pending requests that they merely confirmed (but did not create): [1](#0-0) 

Compare this to `confirm()`, which simply counts entries in the `confirmations` `HashSet<String>` against the fixed `num_confirmations` threshold, with no re-validation that every confirming entry is still a current member: [2](#0-1) 

The same gap exists in the older `multisig/src/lib.rs`: `DeleteKey` only removes requests where `r.signer_pk == pk` (requests originated by that key), not confirmations that key placed on other pending requests: [3](#0-2) 

### Exploitation sketch

1. Members `A, B, C, D` with `num_confirmations = 3`.
2. `A` creates a request (`add_request`). `B` confirms (1), `C` confirms (2) — request stays pending (needs 3).
3. `B` is removed via a `DeleteMember` request (approved through the normal multisig quorum, or `B` voluntarily leaves via a self-request they helped approve before being cut off).
4. `delete_member` only cleans up requests *B created*; it does not strip `B`'s stale confirmation from `A`'s pending request. `B`'s ghost confirmation remains in `confirmations`.
5. `D` (a current, live member) confirms — `confirmations.len() + 1 >= num_confirmations` (3) is satisfied using `B`'s stale vote plus `C` and `D`, and the request executes via `execute_request`, even though only 2 *current* members (`C`, `D`) actually approved it.

This mirrors the oDAO analog precisely: quorum accounting is based on a threshold, while the underlying confirming set is not synchronized with current membership after removal.

### Title
Stale confirmations from removed multisig members still count toward execution threshold - (File: multisig2/src/lib.rs)

### Summary
`delete_member()` removes a member and deletes only the requests *they created*, but leaves their prior confirmations intact on any other pending request. Since `confirm()` counts raw entries in the `confirmations` set against a fixed `num_confirmations` threshold with no liveness check, a removed member's vote can still supply one of the required confirmations, letting a request execute with fewer *current* member approvals than the configured quorum intends.

### Finding Description
`confirm()` compares `confirmations.len() + 1` against `self.num_confirmations` without validating that each address/key in `confirmations` is still `self.members.contains(...)`: [4](#0-3) . `delete_member()` removes the departing member from `self.members` and cleans up requests they authored, but performs no sweep of the `confirmations` map for requests authored by *other* members that the departing member had previously confirmed: [5](#0-4) . Consequently, a stale confirmation from an ex-member is indistinguishable from a live one and is counted toward quorum forever (or until that specific request is executed/deleted).

### Impact Explanation
This allows execution of a multisig request — including `Transfer`, `FunctionCall`, `AddMember`, `DeployContract`, etc. — with fewer live-member approvals than `num_confirmations` requires, undermining the fundamental K-of-N security guarantee of the multisig. Funds controlled by the multisig account can be transferred with effectively reduced real consensus, matching "Critical: Unauthorized transfer... through accounting failure" in the scoped impact list.

### Likelihood Explanation
Requires a member to confirm a pending request and subsequently be removed (voluntarily or via governance) while that request is still outstanding — a realistic sequence given `REQUEST_COOLDOWN`-gated deletion and the fact that removal is a routine multisig operation. No privileged bypass is needed beyond normal governance actions already available in the contract's own state machine.

### Recommendation
On member removal, iterate all pending requests' `confirmations` sets and strip any entry matching the removed member (or, alternatively, re-validate confirming membership at `confirm()`/execution time by filtering the stored confirmation set against `self.members` before counting).

### Proof of Concept
1. Deploy `multisig2` with members `[A, B, C, D]`, `num_confirmations = 3`.
2. `A` calls `add_request` (no auto-confirm) for a `Transfer`.
3. `B` calls `confirm(request_id)` → 1 confirmation.
4. `C` calls `confirm(request_id)` → 2 confirmations (not yet executed).
5. Multisig executes a separate, already-approved `DeleteMember { member: B }` request, removing `B` from `self.members` — per `delete_member`, only requests where `r.member == B` are cleaned up; the transfer request created by `A` is untouched, so `B`'s confirmation remains in its `confirmations` set.
6. `D` calls `confirm(request_id)` → `confirmations.len() + 1 == 3 >= num_confirmations`, triggering `execute_request`, even though only `C` and `D` are current members who actually approved it.

### Citations

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
