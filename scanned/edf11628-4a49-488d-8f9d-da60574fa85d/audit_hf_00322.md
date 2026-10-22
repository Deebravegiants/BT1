# [M] Rogue pool in Shelter

## Summary
Severity: Medium
Contest weight: 0.1865
Dataset id: 1581
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a logic flaw in the Shelter contract that allows a privileged client to repeatedly invoke the activate function on a token that has already been activated. Each call overwrites the stored activation timestamp, effectively resetting the start of the grace period. Because withdrawal is only permitted after the expression activated[_token] + GRACE_PERIOD is less than the current block timestamp, an attacker can keep extending the grace period by re‑activating the token just before it would expire. This prevents honest users from calling withdraw, while the same condition in the deactivate function (activated[_token] + GRACE_PERIOD > block.timestamp) remains true, enabling the attacker to call deactivate and drain all tokens that were deposited through the donate function. The issue manifests when a malicious admin repeatedly activates a token after users have deposited, then deactivates to collect the funds. From a user’s perspective the UI would show a successful deposit but later the user would see no ability to claim the funds and the balance would appear unchanged or disappear after the attacker’s deactivation. The root cause is the lack of a guard against multiple activations and an asymmetric time check that treats activation and deactivation differently, breaking the intended accounting model where funds are locked for a fixed grace period before becoming withdrawable. The bug was uncovered during an audit when the warden demonstrated a concrete exploit sequence: activate token, users donate, activate again many times, more users donate, then deactivate to capture all tokens. It is hard to notice because the contract’s interface does not explicitly forbid re‑activation, and the timestamp update appears benign. To remediate, the contract should enforce a single activation per token, reject subsequent activate calls, allow deactivation only after the grace period has elapsed, and ensure that both withdraw and deactivate functions use consistent time‑based conditions. By correcting the state‑transition logic, the protocol can preserve user deposits and uphold the promised escrow behaviour.

## Proof of Concept
Shelter `client` can call `activate` on an already activated token, this will reset its start time, so if the client activate a token when it `GRACE_PERIOD` is almost finished, it will reset this time.  
This will prevent the user to call `withdraw` because the condition `activated[_token] + GRACE_PERIOD < block.timestamp` but will allow the client to call `deactivate` and receive all funds from the users because it will satisfy the condition `activated[_token] + GRACE_PERIOD > block.timestamp`.

Steps:

* client `activate` tokenA.
* Users deposit tokenA using `donate`.
* client `activate` tokenA again until they has enough tokens.
* More users use `donate`.
* client deactivate tokenA and receive all tokens.

## Recommendation
* Avoid `activate` twice for the same token
* `donate` only after the `GRACE_PERIOD`

I believe the finding to be valid. The warden has shown how the Shelter design allows the client to repeatedly call `activate` to prevent anyone from withdrawing the tokens.

Because this is contingent on a malicious admin, I believe Medium Severity to be more appropriate.
