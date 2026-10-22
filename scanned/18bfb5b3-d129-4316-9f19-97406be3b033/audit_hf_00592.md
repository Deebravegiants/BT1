# [C] C-01 | Inﬂation Attack Steals First Deposit

## Summary
Severity: Critical
Contest weight: 0.2541
Dataset id: 2090
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An inﬂation attack, commonly seen in ERC-4626 vaults, allows a malicious actor to steal deposits
from the ﬁrst depositor. This vulnerability exists in the collateral pool and can be executed as
follows:
• The attacker deposits 1 wei of liquidity into the pool (e.g., ARB).
• The attacker observes a victim placing a liquidity order for 1000 ARB.
• The attacker front-runs the victim and donates 1000 ARB using the donateLiquidity function,
inﬂating the lpPrice.
• The broker ﬁlls the victim's liquidity order, but due to the inﬂated lpPrice, the victim receives 0
shares.
• The attacker withdraws their shares, reclaiming the donated amount along with the victim's
deposit.
The two-step order ﬂow allows for 'front-running' which is usually not feasible on Arbitrum. This
attack is also feasible only with 18-decimal tokens due to the _toWad conversion in addLiquidity.

## Proof of Concept
https://github.com/GuardianAudits/mux-1/pull/3/files#diff-385551754ec84f68ca32ad33b64d6a3edafa70e7815a17f8be68c020b40d3b51R278

## Recommendation
Introduce a minimum share issuance threshold to ensure that deposits always result in a non-zero
share allocation. Consider restricting the donateLiquidity function to privileged accounts.
