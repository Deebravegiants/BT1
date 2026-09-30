# [H] withdrawal queue requestprice can be frontrun in case of defaults

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23304
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When processingMode == ProcessingMode.RequestPrice in AccountableWithdrawalQueue, a redeem request’s value is fixed at the request-time share price. The request is later processed potentially at a very different price.

Impact: * Normal operation: Requesters are typically disadvantaged because price usually rises as interest accrues. Locking at request time forfeits subsequent gains.  
• Defaults: Requesters can front‑run defaults by submitting withdrawals just before delinquency/default and keep the pre‑default higher price, draining liquidity and pushing losses onto remaining LPs. This worsens loss socialization precisely when fairness matters most.

## Recommendation
Consider removing ProcessingMode.RequestPrice (and AccountableWithdrawalQueue .processingMode all together) so redemption value is always determined at processing time.  
Alternatively implement a safeguard for large price movements that will invalidate the redeem request.
