# [M] Implement pyth confidence interval check

## Summary
Severity: Medium
Contest weight: 0.0941
Dataset id: 5331
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently, the system uses price data from Pyth without explicitly checking if the price falls within the provided confidence interval. This could lead to using potentially unreliable price data in volatile market conditions or during unusual events. Impact: • Risk of using inaccurate or unreliable price data. • Potential for financial loss or system instability during high market volatility. • Missed opportunity to implement protective measures for users during uncertain market conditions.

## Recommendation
Implement a check to ensure the price falls within the confidence interval provided by Pyth. If the price is outside this interval or if the interval is unusually wide, take appropriate action (e.g., use a conservative price, pause certain operations). Check ‘Pyth's confidence intervals documentation.
