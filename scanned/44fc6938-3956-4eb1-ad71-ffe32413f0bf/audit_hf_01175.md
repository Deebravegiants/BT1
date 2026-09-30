# [M] Donation attack using agentToken shifts the bonding curve

## Summary
Severity: Medium
Contest weight: 0.0874
Dataset id: 5046
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The buyTokens and sellTokens (subsequently calculateSellReturn) methods of the Agent contract rely on the actual balance of agentToken in the contract using balanceOf to determine the current buy/sell price according to the bonding curve. However, the actual balance and therefore the price calculation can be manipulated by donating agentToken to the contract.

Impact Explanation:  
Medium: The bonding curve is shifted, i.e. buy prices as well as sell prices become lower than expected and intended.

## Recommendation
It is recommended to rely on internal accounting of the agentToken balance instead of using balanceOf to avoid manipulation of the balance used for price calculation.
