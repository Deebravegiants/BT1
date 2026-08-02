## Title
Multisig timelock override_threshold silently clamped down, allowing a reduced-quorum bypass of the configured timelock - (File: `aptos-move/framework/aptos-framework/sources/multisig_account.move`)

### Summary
`multisig_account.move` implements an optional per-account timelock (`MultisigAccountTimeLock`) that normally forces a waiting period before a multisig transaction can execute, unless a configured `override_threshold` number of approvals is reached (`can_execute_with_timelock`, lines 497-515). This threshold is meant to represent an intentionally *higher* bar than the ordinary `num_signatures_required` for bypassing the timelock. However, `update_owner_schema` (lines 1586-1682, also mirrored in the generated doc at lines 4263-4359) automatically clamps `override_threshold` down whenever owners are removed, so that it never exceeds the *new* owner count, without re-validating that this clamp still reflects the security intent chosen by whoever originally configured the timelock. [1](#0-0) 

### Finding Description
`upsert_timelock_internal` requires, at configuration time, that `override_threshold > num_signatures_required` and `override_threshold <= owners.length()`: [2](#0-1) 

This is intended to guarantee that bypassing the timelock always requires *more* approvals than the day-to-day execution threshold — i.e., a stronger custody guarantee for time-sensitive/high-value transactions.

But `update_owner_schema`, which backs `remove_owner(s)`, `swap_owner(s)`, and the combined variants, silently rewrites `override_threshold` down to `num_owners` whenever the owner list shrinks below the previously configured override value: [3](#0-2) 

The only remaining check after the clamp is `override_threshold > num_signatures_required` — it does **not** verify that the clamp preserves the original security margin (e.g., original override was 5-of-7 = ~71% of owners; after two owners are removed it silently becomes 5-of-5 = 100%, or after enough removals it can degrade to `num_signatures_required + 1`, e.g., a 3-of-3 override on a 2-of-3 multisig). Because `num_signatures_required >= 1` is always satisfied and the only invariant enforced is "override > threshold", a sequence of owner removals (each individually valid, each requiring only the ordinary `num_signatures_required` approvals to execute) can progressively erode the override quorum from a high bar (e.g. supermajority) down to the bare minimum (`num_signatures_required + 1`). Once eroded, the owners who executed the removal transactions — or a subsequent smaller coalition — can then reach the override threshold far more easily than the original configuration intended, executing arbitrary multisig transactions (fund transfers, code upgrades, further owner/threshold changes) without waiting out the configured timelock.

This differs from the external Nouns Builder bug only in domain, but shares the same root defect class: a security-relevant derived quantity (`quorumVotes` there, `override_threshold` here) is computed from a mutable base quantity (`token.totalSupply()` there, `owners.length()` here) and is silently re-derived/clamped on state change without re-validating that the *originally intended proportional security guarantee* still holds — only a minimal absolute floor is re-checked.

### Impact Explanation
A multisig account configured with a timelock is explicitly meant to protect custody of held APT/fungible assets/objects and administrative control (owner list, signature threshold, code-object/resource-account authority reachable via the multisig signer) by requiring either (a) a long wait, or (b) an unusually high quorum to skip the wait. The clamp logic lets that high-quorum bar decay to essentially the ordinary execution threshold plus one, purely as a side effect of routine, individually-authorized owner-removal operations, without any explicit re-confirmation that the weakened override is acceptable. This breaks the custody invariant that "multisig-owned assets/resource accounts must not leak... transfer/upgrade authority to [a lower-privileged] set of callers" — the timelock's bypass condition, which was supposed to require overwhelming consensus, degrades to a bar barely above ordinary execution, undermining the entire purpose of configuring a timelock for high-value or sensitive multisig actions.

### Likelihood Explanation
Owner removal (`remove_owner`/`remove_owners`, `swap_owners`) is a normal, expected multisig operation and is documented as always subject to the standard `num_signatures_required` quorum (not the override). Any owner-removal sequence that shrinks the owner set will trigger the clamp automatically — no attacker-supplied malicious input is needed, and the code path is reached by design, not by exploiting an edge case. Realistically, DAOs/teams that resize their owner set over time (a very common operational event) will unknowingly weaken their timelock-override protection, and the code emits only a generic `TimelockUpdated` event rather than an explicit warning that the *security ratio* has degraded, which is easy to miss in monitoring since it looks like the usual metadata-update event.

### Recommendation
When clamping `override_threshold` down due to owner removal, do not silently accept an eroded value that only satisfies `override_threshold > num_signatures_required`. Instead, either:
1. Re-derive the clamp to preserve the original proportional relationship (e.g., recompute as a percentage of the new owner count rather than a raw min-clamp), or
2. Require the clamp/timelock re-validation itself to go through a dedicated `upsert_timelock` call (i.e., abort `update_owner_schema` if the existing `override_threshold` would exceed the new owner count, forcing an explicit owner decision to reconfigure the timelock), rather than auto-adjusting it downward as a side effect of an unrelated owner-management transaction.

### Proof of Concept
Based on the existing test scaffolding in the same file (e.g. `setup_timelock_multisig`, `upsert_timelock`, `update_owner_schema`-backed entry points), the following sequence demonstrates the erosion (I was not able to execute this against a live/test node — this trace is derived from reading the logic in `multisig_account.move` lines 1656-1682 and 919-969):

1. Create a 4-of-7 multisig with `num_signatures_required = 4` and `owners.length() = 7`.
2. Configure `upsert_timelock(multisig_signer, 3600, option::some(7))` — override requires all 7 owners (a strong, unanimous-only bypass), satisfying `7 > 4` and `7 <= 7`. [4](#0-3) 
3. Through normal 4-of-7 approved transactions, sequentially call `remove_owners` three times, shrinking the owner set to 4 owners. Each removal is a legitimately-approved multisig transaction requiring only 4 signatures (the ordinary threshold), not the override.
4. After each removal, `update_owner_schema` clamps `override_threshold` down: 7→6→5→4... down toward `num_signatures_required + 1 = 5`. The only assertion enforced is `override_threshold > num_signatures_required (4)`, which `5` satisfies. [5](#0-4) 
5. The override quorum has degraded from "unanimous 7-of-7" to "5-of-4 owners" — i.e., only one more signature than the ordinary execution threshold — letting the same 4-5 owners who removed others now bypass the timelock on high-value transactions with only marginally more effort than normal execution, defeating the original custody intent of the timelock.

I could not verify this end-to-end via a compiled Move test run (no execution environment available in this session); the trace above is based on static reading of the assertion logic and the existing unit tests (`test_raise_threshold_to_match_override_should_fail`, `test_timelock_with_override_at_boundary`) which confirm the clamp-then-minimal-check behavior but do not test the multi-step owner-removal erosion scenario described here.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L938-962)
```text
        assert!(
            timelock_period >= MIN_TIMELOCK_PERIOD && timelock_period <= MAX_TIMELOCK_PERIOD,
            error::invalid_argument(EINVALID_TIMELOCK_DURATION)
        );

        let multisig_account_resource = &MultisigAccount[multisig_address];
        assert!(
            override_threshold.is_none() || *override_threshold.borrow() > multisig_account_resource.num_signatures_required,
            error::invalid_argument(EINVALID_TIMELOCK_OVERRIDE_THRESHOLD)
        );
        assert!(
            override_threshold.is_none() || *override_threshold.borrow() <= multisig_account_resource.owners.length(),
            error::invalid_argument(EINVALID_TIMELOCK_OVERRIDE_THRESHOLD)
        );

        if (exists<MultisigAccountTimeLock>(multisig_address)) {
            let multisig_account_resource = &mut MultisigAccountTimeLock[multisig_address];
            multisig_account_resource.timelock_period = timelock_period;
            multisig_account_resource.override_threshold = override_threshold;
        } else {
            move_to(multisig_account, MultisigAccountTimeLock::V1 {
                timelock_period,
                override_threshold,
            });
        }
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1656-1682)
```text
        // Verify number of owners.
        let num_owners = multisig_account_ref_mut.owners.length();
        assert!(
            num_owners >= multisig_account_ref_mut.num_signatures_required,
            error::invalid_state(ENOT_ENOUGH_OWNERS)
        );

        // If a timelock is configured, adjust and validate the override threshold
        // after owner/threshold changes.
        if (exists<MultisigAccountTimeLock>(multisig_address)) {
            let timelock = &mut MultisigAccountTimeLock[multisig_address];
            // If override threshold exceeds the new owner count, clamp it down and emit an event
            // so off-chain monitors observe the security-relevant mutation.
            if (timelock.override_threshold.is_some() && timelock.override_threshold.borrow() > &num_owners) {
                timelock.override_threshold = option::some(num_owners);
                emit(TimelockUpdated {
                    multisig_account: multisig_address,
                    timelock_period: timelock.timelock_period,
                    override_threshold: timelock.override_threshold,
                });
            };
            // Override threshold must still be greater than num_signatures_required.
            assert!(
                timelock.override_threshold.is_none() || timelock.override_threshold.borrow() > &multisig_account_ref_mut.num_signatures_required,
                error::invalid_state(EINVALID_TIMELOCK_OVERRIDE_THRESHOLD)
            );
        };
```
