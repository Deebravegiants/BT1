# [M] Sharwa.Finance incident: According to a BlockSec Phalcon alert, Sharwa.Finance disclosed that it had suffered an attack and subsequently suspended operatio

## Summary
Severity: Medium
Target: Sharwa.Finance
Loss: $ 146,000
Attack method: Contract Vulnerability
Published: 2025-10-20
Source: https://x.com/phalcon_xyz/status/1980219745480946087?s=46
Type: slowmist-incident

## Details
According to a BlockSec Phalcon alert, Sharwa.Finance disclosed that it had suffered an attack and subsequently suspended operations. However, several hours later, multiple suspicious transactions occurred again, suggesting that the attacker might have exploited the same underlying vulnerability through slightly different attack paths.In general, the attacker first created a margin account, then used the provided collateral to borrow additional assets through leveraged lending, and finally launched a sandwich attack targeting the swap operations involving the borrowed assets.
The root cause appears to lie in the lack of a bankruptcy check in the swap() function of the MarginTrading contract. This function is responsible for swapping borrowed assets from one token (e.g., WBTC) to another (e.g., USDC). It verifies solvency only once — based on the account state at the start of the swap — before executing the asset exchange, leaving room for manipulation during the process.Attacker 1 (address starting with 0xd356) conducted multiple attacks, earning approximately USD 61,000, while Attacker 2 (address starting with 0xaa24) executed a single attack, gaining around USD 85,000.
