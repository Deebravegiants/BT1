# [H] H-01 | Auto-Compounding Can Lead To Liquidations

## Summary
Severity: High
Contest weight: 0.2131
Dataset id: 2153
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The auto-compounding feature should help borrowers be more capital efficient by automatically reinvesting fees earned on uniswap. As the caller of the reinvest function receives a bounty for doing the work, the position's collateral value decreases through auto-compounding. The reinvest function does not implement safety checks for the position's health. Therefore, it is possible that calling the reinvest function leads to positions being liquidatable, which is definitely not in the borrower's interest and should therefore be prevented. It is also possible to auto-compound liquidatable positions and therefore potentially make them go underwater.

## Proof of Concept
https://github.com/GuardianAudits/impermax-1/blob/POC_REINVEST_LIQUIDATABLE/test/guardian/POC.sol

## Recommendation
Revert at the end of the reinvest flow if the position is liquidatable. It would also make sense to let borrowers decide up to which point they want to auto-compound so that reinvestors can not push them to the edge of liquidation.
