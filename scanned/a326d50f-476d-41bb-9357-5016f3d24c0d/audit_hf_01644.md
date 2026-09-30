# [H] Lack of slippage protection in buyToken() and sellToken() leads to sandwich attacks and potential loss of funds

## Summary
Severity: High
Contest weight: 0.2848
Dataset id: 8795
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The HotCurves contract utilizes a bonding curve with the standard constant product formula (k = x * y) to determine token prices during buy and sell transactions. This means that when tokens are purchased, their price increases, and when they are sold, their price decreases. The buyToken() and sellToken() functions lack slippage protection, making transactions vulnerable to sandwich attacks where a malicious user can manipulate the execution price, leading to unexpectedly high costs or loss of funds for regular users. The following is an example of how such an attack occurs:  
1) A malicious user detects a buy transaction in the mempool. They frontrun this transaction by executing their own purchase first, artificially inflating the token price.  
2) The regular user's transaction is then executed, but at a higher price, causing them to receive fewer tokens for their ETH than expected and potentially incurring significant financial loss.  
3) The malicious user sells the tokens acquired in step 1 at the inflated price, securing a risk-free profit at the expense of the regular user, who has overpaid due to the manipulated price.  
Such an attack can also be executed during token sales.

## Recommendation
This issue can be mitigated by introducing slippage protection using a parameter that specifies the minimum number of tokens the user must receive for the transaction to succeed. This prevents users from executing trades at highly unfavorable rates and protects against unexpected fund losses due to manipulated prices.
