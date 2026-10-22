# [H] H-07 | Users Can Be Charged Extra Fees

## Summary
Severity: High
Contest weight: 0.3483
Dataset id: 21947
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When creating an increase order for a deposit the amountIn is assigned to the collateralToken
balance of the vault, however the user may have only deposited a portion of these tokens.
Indeed when a user receives shares for their deposited amount, the minted shares are computed
only based on the depositInfo[counter].amount and does not include any additional balance that may
have been used to create the order.
However the user pays fees for the balance which was not a direct part of their deposit. A malicious
actor may leverage this to cause the afterOrderExecution execution to revert by forcing the
feeAmount to be larger than the depositInfo[counter].amount.
Consider the following example:
• The vault holds a 5x Long position in GMX
• User A deposits the minimum deposit amount of 10 USDC
• The positionFeeFactor fee in GMX is 30 basis points
• User A then donates 990 USDC to the vault before the next action is run
• The keeper runs the next action and initiates a GMX increase order for $1,000 * 5x leverage =
$5,000 sizeDeltaUsd
• The order is executed and the order fee is 0.003 * 5,000 = $15
• The $15 fee is larger than the user’s actual deposit amount which is stored in the
depositInfo[counter].amount
• An underﬂow occurs when attempting to compute the value to mint based on:
depositInfo[counter].amount - feeAmount = 10 - 15
As a result the active increase order is not recorded as completing in Gamma’s vault and the deposit
ﬂow is never completed, locking all user deposits. A malicious actor only needs to spend $1,000 in
this example and could proﬁt off of this activity by short-selling the GAMMA token and spreading
negative press about the loss of funds for users.

## Recommendation
Consider only charging the fee that the user’s deposit amount would directly be responsible for when
determining the user’s shares amount. Otherwise consider only creating an increase order for the
amount of USDC that the user deposited rather than the entire vault balance.
