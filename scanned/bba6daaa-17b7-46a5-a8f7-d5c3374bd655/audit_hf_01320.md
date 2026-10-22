# [H] H-3 Protect CPOOLs in PoolFactory

## Summary
Severity: High
Contest weight: 0.0580
Dataset id: 6509
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the PoolFactory contract where a generic sweep function is exposed that permits the caller to transfer any ERC20 token held by the factory, including the CPOOL token that is used to pay user rewards. The root cause is the lack of a restriction or access control that distinguishes between stray tokens and the reward token; the sweep logic simply iterates over a token address supplied by the caller and moves the entire balance to the caller’s address. An attacker who can invoke this function—typically the contract owner or any address granted the sweep role—can call it with the CPOOL token address after the factory has accumulated reward balances. By doing so the attacker withdraws all CPOOL tokens from the factory, effectively emptying the pool of reward funds. When a legitimate user later attempts to claim their reward, the claim transaction either returns zero tokens or reverts because the factory no longer holds any CPOOL to distribute. From the user’s perspective the UI shows that a reward is pending but the received amount is zero, or the claim button fails without a clear error, leading to confusion and loss of expected earnings. The issue was discovered during a manual audit of the factory’s token management functions, where the auditor noted that the sweep routine does not filter out the protocol’s own reward token. This bug can be hard to notice because sweep functions are commonly used for recovering accidentally sent tokens, and developers may assume that only non‑essential tokens will be targeted. The flaw violates the accounting assumption that reward tokens remain locked in the factory until distributed, breaking the protocol’s economic guarantees. To remediate, the sweep function should either be removed or hardened by adding an explicit check that rejects the CPOOL token address, and by limiting the caller to a highly trusted role with multi‑sig or timelock protection. In broader terms, this is a classic “unrestricted token sweep” or “withdrawal of privileged assets” bug where privileged assets are mistakenly treated as generic recoverable tokens, leading to potential fund loss and broken reward logic.

## Recommendation
We recommended protecting CPOOL to avoid sweeping.
