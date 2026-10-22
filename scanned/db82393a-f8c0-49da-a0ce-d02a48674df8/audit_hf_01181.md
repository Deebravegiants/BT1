# [H] Insufficient Reserve Enforcement May Block LP Creation

## Summary
Severity: High
Contest weight: 0.6123
Dataset id: 5058
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Agent contract, a portion of the token supply is reserved for liquidity pool initialization via the createLPPosition function. This reserve is defined by:  
```solidity
agentToken.totalSupply() * lpInitialTokenPercentage
```  
However, the contract currently does not enforce a lower bound on trades to ensure that this amount remains available. As a result, users can continue to purchase tokens until the contract’s balance falls below the required LP reserve, effectively locking the system in an unrecoverable state.  
If this condition is met:  
• Calls to createLPPosition() will revert due to insufficient token balance, rendering LP formation impossible.  
• For agents with automaticLPCreation enabled, this will cause any flag-triggered LP creation (such as from isMarketCapReached) to fail.  
• The system will be permanently stuck without the ability to initialize liquidity, and any future buy will continue reducing the balance unless manually halted.  
This scenario doesn't require malicious intent — it can occur naturally if the last buyer is unaware of the LP requirement and the code allows a purchase that drops below the LP threshold.

Impact Explanation:  
High, because the inability to create the LP position halts the full lifecycle of the agent. Without LP creation, token trading mechanisms break down, and any downstream integrations relying on price discovery or secondary market liquidity will fail.

## Recommendation
Introduce a pre-check in the token purchase logic to ensure that no trade is allowed if the resulting token balance would fall below the LP reserve threshold.  
This preserves the LP reserve and guarantees that createLPPosition() can always succeed when triggered. As an added safeguard, consider emitting an event when this limit is near, to alert frontends or off-chain systems that LP initialization is approaching and must be handled with care.
