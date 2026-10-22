# [M] Only the `state`

## Summary
Severity: Medium
Contest weight: 0.1359
Dataset id: 10191
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the governance contract's `state()` accessor, which is intended to return the current lifecycle status of any proposal identified by its `proposalId`. A logical error in the require statement `require(proposalCount >= proposalId && proposalId > initialProposalId, "GovernorBravo::state: invalid proposal id");` unintentionally restricts successful calls to only the most recent proposal. The root cause is an incorrect assumption that `proposalId` increments linearly in lockstep with the global `proposalCount`, an invariant that is not enforced elsewhere in the code. Because the condition checks that the total number of proposals (`proposalCount`) be greater than or equal to the queried identifier, and because `proposalCount` always reflects the latest proposal, older identifiers satisfy the inequality but the subsequent logic inside `state()` only evaluates the state of the latest proposal stored in a single slot, effectively discarding earlier entries. This mismatch makes the function return either an incorrect state or revert for any proposal that is not the newest, preventing callers from reliably querying or confirming the status of pending or executed proposals.

Exploitation is straightforward: an attacker can submit a new proposal, thereby incrementing `proposalCount`, and thereby render all previously submitted proposals invisible to the `state()` function. Since the `execute()` routine relies on `state()` to confirm that a proposal has reached the "Succeeded" phase before it can be executed, the governance system becomes limited to executing at most one proposal at a time. In practice, this can be used to stall the protocol, block critical upgrades, or create a denial‑of‑service condition where legitimate governance actions are never observed as executable. From a user's perspective the symptoms are confusing: a governance participant may observe that their proposal never reaches an executable state, that the UI shows no status update, or that calls to `state(proposalId)` return an unexpected value such as "Pending" for a proposal that has already been voted on.

The issue was discovered during a formal security audit when reviewers examined the conditional guard of `state()` and noticed the inconsistency between the intended range check and the actual storage layout. It is hard to notice in normal testing because the function does not revert for the latest proposal, giving the appearance that the contract works correctly for recent actions, while older proposals silently become inaccessible. This hidden failure mode violates fundamental governance accounting assumptions: each proposal should have an independently tracked lifecycle state, and the ability to query that state must be reliable for any identifier.

The recommended remediation is to enforce the intended linear relationship between `proposalId` and `proposalCount` or, more directly, adjust the require clause to `require(proposalId <= proposalCount && proposalId > initialProposalId, ...)`. Additionally, the storage of proposal states should be indexed by `proposalId` rather than a single mutable slot, ensuring that each proposal’s state is recorded and retrievable independently. After fixing, any participant will be able to query the correct status of any proposal, and the `execute()` function will correctly identify executable proposals, restoring the intended multi‑proposal concurrency of the Governor contract.

## Proof of Concept
require(proposalCount >= proposalId && proposalId > initialProposalId, "GovernorBravo::state: invalid proposal id");

Currently `proposalCount` needs to be bigger or equal to `proposalId`.  
Assuming `proposalId` is incremented linearly in conjunction with `proposalCount`, this implies only the most recent `proposalId` will pass the `require()` check above. All other proposals will not be able to have their states checked via this function.

## Recommendation
Change above function to `proposalCount <= proposalId` (assuming `proposalId` is set linearly, which currently is not enforced by code).

The warden has shown how, due to a mistake in logic, only the `state` of the latest proposal can be read.

Because the function `state` is used in `execute` we can conclude that only one proposal can be queue for execution at a time, drastically reducing the availability of the Governor.

For this reason I believe medium severity is appropriate.
