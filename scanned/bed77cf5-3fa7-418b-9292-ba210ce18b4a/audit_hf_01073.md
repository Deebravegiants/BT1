# [M] PAIR-1 | Diluted Dividends

## Summary
Severity: Medium
Contest weight: 0.0423
Dataset id: 4084
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a dividend dilution flaw in the BridgesPair contract where the contract’s own reward balance is ignored when adjusting rewardDebt on line 232, but the same balance is still included in the magnifiedDividendPerShare calculation. The root cause is that the contract does not subtract the BridgesPair token balance from the totalSupply used to compute the per‑share dividend amount, even though the rewards have been accounted for elsewhere. An attacker can trigger this condition by depositing tokens that generate a reward balance in the BridgesPair contract; the contract will then credit the attacker’s rewardDebt, effectively removing those rewards from the pool, while the dividend per share is still divided by the full totalSupply. Consequently, every other holder receives a smaller share of the dividend than they are entitled to, leading to a systematic loss of expected earnings. This issue manifests whenever the BridgesPair contract holds a non‑zero reward balance – typically after a reward distribution event – and it affects all token holders who rely on the dividend mechanism, including regular users and the protocol’s economic model. The problem was discovered during a manual audit that compared the rewardDebt adjustment with the dividend per‑share formula and noticed the mismatch. It can be hard to notice because the contract’s state variables appear consistent and the UI may still display a dividend rate, yet the actual transferred amounts are lower than the calculated rate, creating a silent erosion of funds. To remediate the issue, the calculation of magnifiedDividendPerShare should exclude the BridgesPair’s own balance by subtracting that balance from totalSupply (as suggested on line 229), ensuring that only the tokens owned by external holders contribute to the dividend pool. This aligns the accounting with the intended business logic that dividends are distributed proportionally to genuine token holders and prevents the dilution of payouts.

## Recommendation
Subtract the BridgesPair’s balance from the totalSupply on line 229.
