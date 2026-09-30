# [M] Missing slippage protection on

## Summary
Severity: Medium
Contest weight: 0.1727
Dataset id: 1896
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ReputationMarket contract provides preview functions (simulateBuy() and simulateSell()) to estimate outcomes before actual transactions (buyVotes() and sellVotes()). While buyVotes() includes slippage protection against price changes between simulation and execution, sellVotes() lacks this safeguard. While Base L2's private mempool prevents traditional frontrunning, users are still exposed to two risks:  
1. Market volatility between simulation and execution could result in receiving fewer funds than expected  
2. The sequencer prioritizes transactions with higher fees (ref), allowing users paying higher fees to execute trades first, potentially leading to unfavorable price movements for pending transactions with lower fees.  
sellVotes() is missing slippage protection.

Internal pre-conditions  

External pre-conditions  

Attack Path  
1. User calls simulateSell() to preview expected returns  
2. Market experiences high sell volume, causing price decline  
3. User submits sellVotes() transaction with outdated price expectations  
4. Due to missing slippage protection, transaction executes at significantly lower price than simulated, resulting in unexpected losses

Loss of assets for the affected users.

## Recommendation
Implement a slippage control that allows the users to revert if the amount they received is less than the amount they expected.
