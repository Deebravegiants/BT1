# [H] H-06 | Interest Formula Favours Longer Credits

## Summary
Severity: High
Contest weight: 0.1968
Dataset id: 21501
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol has a credit feature and the interests for these credits are paid upfront. Interest is meant to be linear based on INTEREST_PER_DIEM variable and credit length. However, interest formula favours longer credits due to an error in it. Currently: • Yearly credit interest is ~348.6 * daily interest instead of 365. • Yearly credit interest is ~11.6 * monthly interest instead of 12. This means ~4.5% discount in interest when taking yearly credits. The protocol has two major revenue streams: LP fees and credit interests. This income is used to increase the baseline value of the token. Due to this formula favouring longer credits, protocol loses ~3-5% of it’s expected interest revenue (exact number will be affected by average credit length).

## Recommendation
Update the interest formula to prevent value loss, and ensure the interest rate is fixed regardless of the credit length.
