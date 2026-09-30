# [H] H-09 | IM Validation Incorrectly Attributes Price Impact

## Summary
Severity: High
Contest weight: 0.2624
Dataset id: 2279
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the validateNextPositionEnoughMargin function the ﬁllPremium is computed as if the ﬁll price affected the entire position, when in fact the ﬁllPrice only causes a net change in the position’s margin for the newly added size from the current order. For example:
• Current WETH price is $5,000
• Bob has a long position with size 10 WETH at an entry price of $5,000
• Bob opens an increase long for a size of 1 WETH and is negatively impacted to receive $5,100 as a ﬁll price
• The computed ﬁllPremium is 11 * -100 = -$1,100
• However Bob only received a negative impact of $100
As a result orders which build on top of existing positions will have their negative impact errantly accounted for the existing position size in the initial margin validation, preventing valid orders from being executed. Additionally, orders which ﬂip the side of the position will not be validated for the entire negative price impact that they experience, as only the net position on the opposite side remains. Therefore positions can be opened where they are in fact below the IM since the entire negative price impact has not been accounted for.

## Recommendation
Compute the ﬁllPremium based upon the size delta of the order which is currently being executed instead of the entire size of the new position.
