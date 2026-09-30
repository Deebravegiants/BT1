# [M] Tokens will get stuck if sent to a bot wallet

## Summary
Severity: Medium
Contest weight: 0.0281
Dataset id: 11146
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an asymmetric blacklist restriction in the OrdiswapToken contract that permits tokens to be transferred into an address that has been flagged as a bot, while simultaneously preventing any outbound transfer from that same address. The root cause is a transfer validation routine that only checks the sender against a bot list and does not enforce the same rule on the recipient. Because of this, an attacker or a careless user can send tokens to a blacklisted bot address – for example by using a swap, airdrop, or direct transfer – and the contract will accept the incoming transfer. Once the tokens reside in the bot wallet, any subsequent attempt to move them out fails, as the contract reverts outbound transfers from blacklisted addresses. The impact is that funds become effectively locked: the token holder sees a balance that cannot be spent, the protocol may lose circulating supply, and users experience a mismatch between the expected ability to withdraw or trade tokens and the reality of a zero‑output transaction. This condition occurs whenever an address is added to the bot list and the contract’s transfer function is invoked with that address as the sender, while the same address is allowed as a recipient. The affected parties include token holders who inadvertently send to a bot, any downstream contracts that rely on token movement, and the overall token economics. The issue was discovered during a manual audit of the token’s transfer logic, where the reviewer noticed that the blacklist check was applied only to msg.sender and not to the recipient, a subtle asymmetry that does not raise immediate compile‑time warnings. The bug can be hard to notice because typical test suites focus on preventing transfers to malicious addresses, not on the possibility of locking tokens by sending them to such addresses. To remediate, the contract should enforce symmetric restrictions – either block both inbound and outbound transfers for blacklisted addresses, or provide a safe recovery mechanism (such as an admin‑only forced transfer) that allows tokens to be reclaimed from a bot wallet. Conceptually, this is a blacklist‑logic flaw that results in token lockup, violating the fundamental accounting assumption that any transferred token remains movable by its owner unless explicitly burned. From a user’s perspective the symptom is a balance that appears in their wallet but cannot be spent, leading to situations where “my tokens disappear” or “I cannot withdraw my funds”.

## Recommendation
Recommendation not found
