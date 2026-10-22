# [H] H-4 Actions limits manipulation

## Summary
Severity: High
Contest weight: 0.0677
Dataset id: 3117
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an action‑limit manipulation flaw that allows an attacker to render the contract’s submit and withdraw functions unusable for subsequent users. The contract maintains internal counters that track how many times the submit and withdraw actions have been performed within a certain period or against a global limit. Because the logic that updates these counters does not properly isolate or reset them after each user interaction, an attacker can repeatedly call submit followed by withdraw in a tight loop, incrementing the counters until the predefined limit is reached. Once the limit is exhausted, the contract’s checks reject further calls to submit or withdraw, effectively locking out honest participants. This occurs under normal operating conditions; no special privileges are required beyond being able to invoke the public functions. The impact is that legitimate users attempting to deposit funds or retrieve their balances will encounter transaction reverts or silent failures, leading to a situation where funds appear to be missing or cannot be withdrawn, violating the protocol’s accounting guarantees and user expectations of being able to deposit and later withdraw. The issue was discovered during a manual security audit by MixBytes, which identified that the limit‑checking code could be driven to its boundary through repeated cycles. The bug is subtle because normal usage with a small number of participants does not trigger the limit, making it easy to miss in standard testing. To remediate, the contract should be redesigned so that action limits are scoped per user or per block, include proper reset mechanisms, and enforce that a single actor cannot exhaust a global limit intended for the whole system. In essence, the flaw belongs to the class of quota‑exhaustion or resource‑locking bugs where shared counters can be manipulated to deny service to other participants, breaking the expected flow of funds and undermining trust in the protocol.

## Recommendation
We recommend redesigning the logic to mitigate the risk of action lock-ups.
