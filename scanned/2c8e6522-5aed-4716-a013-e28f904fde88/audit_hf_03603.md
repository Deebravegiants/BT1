# [M] GLOBAL-2 | Incorrect block.timestamp Used

## Summary
Severity: Medium
Contest weight: 0.0455
Dataset id: 19583
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability stems from the governance contracts relying on the native block.timestamp value to determine the current time for proposal deadlines and other time‑sensitive actions. In the GovToken and ProtocolGovernance contracts a helper called CLOCK_MODE checks that the clock function returns block.timestamp, but on layer‑2 networks the block timestamp can drift from the canonical chain time because the execution environment does not enforce strict synchronization with the underlying L1. This drift means that the contract may record a time that is either ahead or behind the true protocol time as reported by Chain.currentTimestamp(). When a proposal is submitted close to its voting deadline, an attacker or even an honest participant can experience a situation where the contract believes the deadline has passed (or not yet passed) based on the inaccurate block.timestamp. Consequently, proposals may be accepted or rejected incorrectly, allowing governance decisions to be taken outside the intended voting window. The impact includes potential bypass of governance safeguards, unauthorized execution of privileged functions, and loss of confidence from token holders because the protocol may appear to ignore its own timing rules. The issue manifests whenever the clock function is called, which is typically during proposal creation, voting, and execution phases, and it affects any user who interacts with the governance system, including token holders, delegators, and the protocol itself. The flaw was discovered during a systematic audit that examined how time is sourced for governance logic and identified that the validation checks only block.timestamp instead of the more reliable Chain.currentTimestamp() source. It can be hard to notice because block.timestamp usually looks plausible and only diverges under specific L2 conditions, making the bug silent until a deadline edge case is hit. To remediate the problem, the contract should replace all uses of block.timestamp in the clock validation and any time‑sensitive calculations with Chain.currentTimestamp(), ensuring that the governance module always references the canonical timestamp provided by the execution environment. This change aligns the contract with the intended accounting assumptions that time progresses uniformly and that proposal windows are enforced accurately, preventing funds from disappearing or decisions being made outside the expected schedule.

## Recommendation
Validate the result of the clock function against the Chain.currentTimestamp().
