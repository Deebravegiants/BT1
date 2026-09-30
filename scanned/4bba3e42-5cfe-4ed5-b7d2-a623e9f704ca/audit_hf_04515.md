# [H] H-01 | validateRequest Errant Price Impact

## Summary
Severity: High
Contest weight: 0.3029
Dataset id: 22078
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the validateRequest function the calculateStartingPnl is computed as if the fill price affected the entire position, when in fact the fillPrice only causes a net change in the position’s margin for the newly added size from the current order. For example:
• Current WETH price is $5,000
• Bob has a long position with size 10 WETH at an entry price of $5,000
• Bob opens an increase long for a size of 1 WETH and is negatively impacted to receive $5,100 as a fill price
• The computed starting pnl is 11 * -100 = -$1,100
• However Bob only received a negative impact of $100 on his order
As a result orders which build on top of existing positions will have their negative impact errantly accounted for the existing position size in the currentAvailableMargin validation, preventing valid orders from being executed. Additionally, orders which flip the side of the position will not be validated for the entire negative price impact that they experience, as only the net position on the opposite side remains. Therefore positions can be opened where they are in fact below the necessary margin since the entire negative price impact has not been accounted for.

## Proof of Concept
https://github.com/GuardianAudits/perps-v3-2/pull/3/files,https://docs.google.com/spreadsheets/d/1QSwF_VodFCIJWr6JXLmmz4wqRkqbtH6QfYkP6os3SWk/edit?gid=0#gid=0

## Recommendation
Compute calculateStartingPnl based upon the size delta of the order which is currently being executed instead of the entire size of the new position.
