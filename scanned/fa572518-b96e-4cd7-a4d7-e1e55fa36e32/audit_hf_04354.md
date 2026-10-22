# [M] M-04 | Lacking _buy Slippage Protection

## Summary
Severity: Medium
Contest weight: 0.0500
Dataset id: 21513
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a missing slippage protection in the contract's internal _buy function that performs a token swap. Because the swap call does not specify a maximum acceptable price impact, an attacker can place a transaction immediately before (front‑run) and after (back‑run) the victim's purchase, forming a sandwich. The attacker manipulates the market price between the two swaps, causing the victim's swap to execute at an unfavorable rate. This can result in the user receiving far fewer tokens than expected, or in extreme cases the swap returning zero output, effectively making the user's funds disappear. The issue arises whenever the _buy function is invoked on a chain where transactions are visible in a public mempool, allowing the attacker to observe and reorder transactions. It affects any participant who calls the buy interface, including regular users and integrators, because the contract assumes the swap will execute at the quoted price. The flaw was discovered during a manual audit of the contract code, where the absence of a slippage parameter or deadline check was noted. The problem is subtle because the transaction may still succeed and emit no error, making the loss appear as a normal outcome rather than a contract failure. The bug belongs to the class of price‑manipulation vulnerabilities caused by unchecked swap parameters. To remediate, the contract should enforce a maximum slippage limit or use a deadline, and optionally query the expected output before executing the swap, reverting if the actual amount deviates beyond an acceptable threshold. Implementing these checks restores the intended accounting guarantees that a user’s purchase yields the expected amount of tokens and prevents the protocol from leaking value through sandwich attacks.

## Recommendation
The system is currently deployed on Blast which does not have a public mempool, so frontrunning sandwich vectors are not an immediate concern. However upon deploying to new chains, carefully consider this risk and implement the necessary swap protections to mitigate the sandwich attack vector.
