# [H] Pool Delegates can set a really high origination fee and steal all pool funds.

## Summary
Severity: High
Contest weight: 0.1591
Dataset id: 10226
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The delegate origination fee can be set to any value at any time and anyone can deploy a loan, so the delegate can receive all the funds of a loan.
Exploit scenario
• gather funds to a pool with a regular origination fee
• given enough funds, increase the origination fee to the pool amount minus the platformOriginationFee (which can be close to zero if the delegate creates the loan with 1 payment interval and 1 number of payments)
• create a fake loan (anyone can deploy a loan) and fund it

## Recommendation
The following mitigation options were proposed:
• Redeploy factory and fix anyone can deploy a loan;
• Set an origination fee limit;
• Don't allow changing the origination fee;
• Set a timelock/minimum withdrawal cycles to change the origination fee;
• Require governor approval on fee change.
