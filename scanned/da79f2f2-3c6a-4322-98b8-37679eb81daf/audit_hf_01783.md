# [H] Borrowing interest is calculated inaccurately and can be manipulated

## Summary
Severity: High
Contest weight: 0.3648
Dataset id: 9806
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The system keeps track of each user's loan and the accrued interest individually. Each user has a corresponding last-update timestamp, which is compared with the current timestamp to calculate the newly accrued interest only when the user's position is updated, e.g., when borrowing funds or repaying debt. The accrued interest during a period is calculated as: interestAccrued = debt * (utilizationRate * baseRate + initRate) * delay / oneYearInMs where utilizationRate = TotalBorrows / (TotalBorrows + Cash), i.e., the market's current utilization rate. The delay variable represents the time difference between the user's current and last actions. However, using the current utilization rate to calculate the interest in the past delay period is incorrect. It assumes that the rate has not been changed since the last user's action, which, however, is not always the case because other users' actions can arbitrarily change the market's state. Consider the following example: 1. t = 0, User A borrows. The utilization rate is 50%. 2. t = 100, User B borrows. The utilization rate becomes 90%. 3. t = 101, User A repays. The interests are calculated using a rate of 90%, but it was 50% most of the time. User A ends up paying more interest. Additionally, an attacker could exploit this design to lower the interest rate to a number close to initRate. Before repaying their debt, they could mint a large number of oTokens with another account to decrease the market's utilization rate as much as possible. After repaying the debt, they redeem the underlying tokens without incurring a loss.

## Recommendation
Based on how the interest is calculated, the system should be designed to update every user's debt whenever the market's utilization rate or the state has changed. Compound V2's design is an example: • Every user has a corresponding interestIndex, and the protocol keeps track of a global borrowIndex. • Before performing any action that will change the market's state, the system accrues interest by increasing the borrowIndex using the formula above. • The user's debt is calculated as borrowBalance * borrowIndex / interestIndex, which updates automatically when the borrowIndex increases. • When a user borrows, their borrowBalance is first updated to include the accrued interest so far and then increased by the borrowed amount. Next, their interestIndex is set to the global borrowIndex. The process is similar when a user repays their debt.
