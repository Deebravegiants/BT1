# [M] Initial mint amount of TRNDO is wrong

## Summary
Severity: Medium
Contest weight: 0.3662
Dataset id: 16051
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of an incorrect initial token minting amount in the constructor of the TornadoBlastBotToken contract. The code uses the literal 10e8 multiplied by the token decimals to mint tokens to the deployer, intending to create a total supply of one hundred million tokens. However, in Solidity the notation 10e8 is interpreted as the floating‑point literal ten times ten to the power of eight, which evaluates to one billion (1,000,000,000) rather than one hundred million (100,000,000). This mis‑calculation originates from a misunderstanding of scientific notation and the fact that Solidity treats the expression as a decimal value before scaling by the decimals factor. Because the constructor runs only once at deployment, the owner receives an excess of nine hundred million tokens. The over‑minted supply can be exploited by the owner or any party that gains control of the owner’s private key to sell or transfer the surplus tokens, diluting the value of legitimate holders, breaking the intended token economics, and potentially eroding trust in the protocol. The impact is a supply inflation that may lead to market manipulation, reduced confidence, and financial loss for users who expected a fixed 100 million token cap. The issue manifests immediately after deployment: users inspecting the total supply or their balances will notice a larger-than‑expected number of tokens, and the share of each holder will be smaller than anticipated. The bug was discovered during a manual audit where the auditor compared the comment “// 100 million” with the actual minted amount and identified the discrepancy. It can be hard to notice because the literal 10e8 visually resembles a concise representation of 100 million, and typical unit tests may not verify the exact supply value. To remediate, the mint expression should be replaced with an explicit integer literal representing the intended amount, such as 100_000_000, multiplied by the decimals factor, thereby aligning the on‑chain supply with the documented token economics and preventing unintended inflation.

## Recommendation
```diff
- _mint(msg.sender, 10e8 * 10 ** decimals()); // 100 million
+ _mint(msg.sender, 100_000_000 * 10 ** decimals()); // 100 million
```
Consider using 100_000_000 instead of 10e8, which is much more readeable:
