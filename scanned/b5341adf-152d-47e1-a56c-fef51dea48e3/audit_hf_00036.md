# [M] GLOBAL-3 | Liquidation Will Fail if Oracle is Down

## Summary
Severity: Medium
Contest weight: 0.1392
Dataset id: 112
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In extreme cases, like when oracles go offline or token prices drop to zero, liquidations can get stuck. This poses serious risks to the protocol's financial health. During these times, it's crucial to allow liquidations to keep the protocol solvent. However, any liquidation-related actions will fail for debt holders of the affected token. For example, Chainlink has stopped their oracles in rare situations, such as the UST collapse, to avoid giving wrong data to protocols. If a token's value crashes or the oracle system breaks down, trying to use the liquidate function will fail. This is because it depends on the oracle's price information. As a result, users with the affected asset won't face liquidations. This can weaken the protocol's response to solvency issues. There's a risk that a user's asset value could drop below their debts. This would remove any reason to liquidate and push the protocol closer to financial trouble.

## Recommendation
Ensure there is a safeguard in place to protect against this possibility. Such as a backup oracle.
