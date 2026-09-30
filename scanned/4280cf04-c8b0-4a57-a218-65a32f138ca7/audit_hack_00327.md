# [M] Secured Finance incident: Secured Finance’s fixed-rate lending protocol was exploited via an order-book accounting flaw that treated unfilled orders as fill

## Summary
Severity: Medium
Target: Secured Finance
Loss: $ 180000
Attack method: Flash Loan Price Manipulation
Published: 2026-09-05
Source: https://x.com/Secured_Fi/status/2097182727992963457
Type: slowmist-incident

## Details
Secured Finance’s fixed-rate lending protocol was exploited via an order-book accounting flaw that treated unfilled orders as filled and created invalid balances. Attackers used flash loans and self-trades to manipulate the current-block price and withdraw funds. Markets on Ethereum, Arbitrum, and Filecoin were paused. The team’s preliminary loss estimate is about $180,000; no recovery has been confirmed.
