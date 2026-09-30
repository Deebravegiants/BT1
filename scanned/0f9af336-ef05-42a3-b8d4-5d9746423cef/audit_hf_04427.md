# [M] M-03 | Slide Causes Anchor To Disappear

## Summary
Severity: Medium
Contest weight: 0.1174
Dataset id: 21903
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the slide function the reserves of the anchor position are added back to the anchor after potentially extending the Anchor further downwards with a call to _updateTicks. This can result in the Anchor position having little liquidity or disappearing entirely after the slide operation. This is because the price may have been set less than or equal to the lower end of the Anchor position, in which case there would be no reserves in the liquidity position. In this case the Anchor position would not be built up again until a sweep occurs, and in the meantime there can be erratic price fluctuations between the floor and discovery which may be far apart.

## Recommendation
In these situations consider keeping the Anchor position to the tickSpacing above the current price so that the Anchor does not entirely disappear, but is not extended below the active price because that would require reserves to be pulled from the floor. Otherwise be aware of this quirk in the system and document it for users and integrators.
