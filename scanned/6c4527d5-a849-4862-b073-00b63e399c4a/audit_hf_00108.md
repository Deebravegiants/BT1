# [M] M-3 Zero Token

## Summary
Severity: Medium
Contest weight: 0.0189
Dataset id: 203
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of an unchecked token address parameter in the constructor of a farming pool contract. The contract accepts an address that is intended to represent an ERC‑20 token used for staking and reward distribution, but it does not verify that this address is non‑zero before storing it. The root cause is a missing validation check (e.g., require(token != address(0))) during contract initialization, which allows a zero address to be injected either accidentally or deliberately. If the contract is deployed with a zero token address, every subsequent call that interacts with the token – such as balance queries, transfers, deposits, withdrawals, or reward calculations – will be directed to address(0). Because address(0) is not a contract, calls to ERC‑20 functions will either silently fail, revert, or be ignored, leading to a situation where users attempting to stake tokens receive no confirmation, deposits appear to succeed but no tokens are recorded, and reward distribution never occurs. From a user’s perspective this manifests as a pool that accepts deposits but never reflects a balance, or a UI that shows a token selection but later returns zero balance or no rewards, creating the impression that "funds disappear" or that a "refund is missing". The impact is that users’ funds may become locked in the pool without any way to retrieve them because the contract cannot correctly reference the intended token contract, effectively burning the assets or making them unrecoverable. The issue surfaces only at deployment time when the constructor is called with an incorrect argument; it can be exploited by any party that can control or influence the constructor parameters, such as a malicious factory contract or a compromised deployment script. The bug is difficult to notice during regular testing because the contract compiles and deploys without error, and only fails when a token‑related operation is performed, which may be exercised later in production. It belongs to the class of "missing input validation" bugs, specifically address‑validation flaws that permit zero‑address injection. To remediate the problem, the constructor should explicitly validate that the token address is not the zero address and revert if the check fails, ensuring that only a valid ERC‑20 contract can be linked. Additional defensive programming, such as using OpenZeppelin's Ownable or Initializable patterns, can further reduce the risk of misconfiguration. By enforcing this check, the contract will align with business logic that assumes a real token contract exists, preserving accounting integrity and preventing silent loss of user funds.

## Recommendation
It is recommended to add a check for non-zero address.
2.4 Low
