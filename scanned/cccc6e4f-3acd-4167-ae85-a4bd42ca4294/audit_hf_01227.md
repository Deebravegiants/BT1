# [M] LP deposit can be DoS

## Summary
Severity: Medium
Contest weight: 0.1931
Dataset id: 5533
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a denial‑of‑service condition affecting the liquidity‑provider (LP) deposit mechanism of the contract. The root cause lies in the way the contract tracks LP participation: it limits the number of LP addresses (lpLimit) but does not enforce a minimum effective stake or risk percentage before an address is counted toward that limit. An attacker can exploit this by creating the maximum number of LP accounts, each depositing the minimum allowed amount (0.1 ETH) and setting an extremely low risk percentage (e.g., 1%). After the deposits are recorded, the attacker immediately withdraws each LP, which resets the risk percentage of every entry to zero. Because the contract updates the total staked LP amount based on the risk percentages, the combined stake collapses to zero while the lpLimit remains fully occupied. Subsequent users are then unable to add new LPs because the limit is considered reached, even though no actual liquidity is available. From a user’s perspective the UI may show that the LP pool is full but the displayed LP stake is zero, leading to confusion and the inability to provide liquidity or earn rewards. The impact is high for the protocol: new liquidity cannot be added, the lottery or other mechanisms that depend on LP stake receive no backing, and the protocol’s revenue model is effectively halted. The issue was discovered during a manual audit that examined edge cases around LP registration and withdrawal logic. It is difficult to notice because the attacker’s deposits are tiny and appear legitimate, and the contract does not emit a clear warning when the total stake drops to zero while the address limit is saturated. To remediate, the contract should either prevent LP entries with a zero effective stake, enforce a minimum risk percentage greater than zero, allow the admin to deactivate or purge LP slots that have zero stake, or redesign the limit logic to count only active, staked LPs rather than all registered addresses. Implementing such checks restores the ability for honest participants to add liquidity and prevents a single actor from locking the LP pool with negligible funds.

## Proof of Concept
1. Attacker creates 100 address (current lpLimit) and calls lpDeposit from each giving 0.1 eth (minLpDeposit). He sets 1% as risk percentage for all.
2. Overall investment by attacker is 0.1eth*100 = 10 eth.
3. In next lottery run, LP are staked since attacker set 1% risk for all 100 LP address so total LP staked would be 10eth* 1% = 0.1 eth.
4. Before the next lottery run, Attacker immediately request to withdraw each LP which sets risk percentage of each to 0.
5. In the next lottery run, LP stakes are updated to 0 (Attacker might incur loss if User wins over LP but loss is limited to <0.1 eth).
6. Now no new LP can deposit as LP limit is reached and LP stakes will be 0 for all future lottery. This will remain case till Attacker calls withdraw.
7. At current rate ~315 USD is all required by Attacker to risk this attack.

## Recommendation
A new function could be added which allows to deactivate LP with riskPercentage and stake as 0 by Admin.
