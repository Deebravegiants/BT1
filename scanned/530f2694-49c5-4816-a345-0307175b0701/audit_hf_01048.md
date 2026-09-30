# [H] MJR-3 Potential re-entrancy problem

## Summary
Severity: High
Contest weight: 0.0141
Dataset id: 4011
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a classic re‑entrancy issue in the profit‑splitting contract. At the point where the contract transfers incoming tokens to the designated recipient, it performs an external call before updating the internal accounting that records how much each participant is owed. Because the state change occurs after the external call, a malicious recipient contract can execute a fallback or receive function that calls back into the profit‑splitting function, causing the same transfer logic to run again before the balance is reduced. This loop can be repeated until the contract’s token reserve is exhausted. The root cause is the violation of the Checks‑Effects‑Interactions pattern and the absence of a re‑entrancy guard such as a nonReentrant modifier. An attacker would need to deploy a contract that implements a token‑receiving callback and, when invoked by the splitter, immediately invokes the splitter’s withdraw or split function again. Under these conditions the attacker can siphon funds that were meant to be split among legitimate participants. The impact is that users who initiate a split may see their expected refund disappear, their balance become zero, or receive less than the calculated share, effectively losing funds. The problem manifests whenever the recipient is a contract capable of executing code on token receipt, which includes many ERC20 implementations that invoke a callback on transfer. All token holders and any party relying on the correct accounting of the splitter are affected. The issue was discovered during a manual security audit by MixBytes, which flagged the line as a potential re‑entrancy point. It can be hard to notice because the external call looks like a normal token transfer and typical unit tests may not include a malicious callback contract. To remediate, the contract should follow the Checks‑Effects‑Interactions pattern by updating balances before making external calls, or it should protect the vulnerable function with a re‑entrancy guard that blocks nested entries. This class of bug is known as a re‑entrancy vulnerability, which breaks the assumption that accounting state is updated atomically with respect to external interactions, leading to money disappearing or refunds failing.

## Recommendation
We recommend to add re-entrancy guard
