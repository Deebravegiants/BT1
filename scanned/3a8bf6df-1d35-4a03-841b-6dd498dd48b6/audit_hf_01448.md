# [H] H-2 Empty trades

## Summary
Severity: High
Contest weight: 0.2286
Dataset id: 7528
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The trade function allows you to specify a price limit, upon reaching which the cycle will be exited without performing any movement of tokens at line Battle.sol#L286, but with a change of the current price at line Battle.sol#L359.  
An attacker creates a contract that calls the trade function of the Battle contract with a price limit. To get passed the balance check, the attacker sends one token to the contract inside tradeCallback.  
This ability to perform empty exchanges in empty areas of liquidity creates the possibility of price manipulation. This capability can be used by an attacker to attack liquidity providers in order to block the addition of liquidity.  
LiquidityManagement.sol#L43  
To resolve this, it is necessary to resort to non-standard actions, for example, adding liquidity over the entire tick interval.  
This error is marked as HIGH as the contract is blocked by the attacker.

## Recommendation
We recommend following one of the next ways:  
1. Revert empty trades  
2. Add function initAddLIquidity that moves price to the right place and then call the addLiquidity function
