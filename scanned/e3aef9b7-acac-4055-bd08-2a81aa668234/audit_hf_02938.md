# [C] Any user can add XP by calling addXP

## Summary
Severity: Critical
Contest weight: 0.0204
Dataset id: 16289
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an unauthorized state‑change bug where the function that adds experience points (XP) to non‑fungible tokens (NFTs) is declared public and lacks any access control. Because the function is publicly callable, any address can invoke it directly and specify an arbitrary amount of XP to be credited to any NFT they own. The root cause is the incorrect visibility modifier; the function was intended to be invoked only by internal contract logic (specifically by returnLoserTicketXPs when a user loses a ticket and should be refunded XP), but the developer left it public, allowing external callers to bypass the intended accounting flow. An attacker can exploit the bug by sending a transaction that calls addXP with a large XP value, thereby inflating the XP balance of their NFT without performing any game action. This leads to a distortion of the protocol’s reward and ranking mechanisms, potentially granting the attacker unearned privileges, higher leaderboard positions, or access to XP‑based rewards. The issue manifests whenever a user interacts with the contract, as there is no condition that restricts the call to trusted code paths; therefore, it can be triggered at any time by any externally owned account. All participants who rely on XP as a measure of achievement or as a prerequisite for other contract features are affected, because the integrity of the XP accounting is compromised. The flaw was discovered during a manual audit that examined function visibility and access patterns. It can be hard to notice because the function appears to be part of the legitimate workflow and may not be called directly by the front‑end, leading reviewers to assume it is only used internally. To remediate the issue, the function should be changed to internal or private, or protected with an appropriate modifier (e.g., onlyOwner, onlyAuthorized) that restricts calls to the contract’s own logic. In conceptual terms, the bug belongs to the class of “unauthorized external function exposure” or “privilege escalation via missing access control”. From a user’s perspective, the symptom is that an NFT suddenly shows a much higher XP balance than expected, and the user may receive rewards they never earned, breaking the trust model of the platform.

## Recommendation
Consider making addXP internal instead of public: Varonve.md
