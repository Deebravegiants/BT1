# [M] M-06 | Shifts Within A Virtual Inventory Unfairly Punished

## Summary
Severity: Medium
Contest weight: 0.1937
Dataset id: 21440
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When shifting between two markets in the same virtual inventory the shift will often experience negative impact from the virtual inventory even though the shift did not cause an imbalance in the virtual inventory token amounts. Consider the following scenario:
• Market A has a longTokenUsd of 200 and a shortTokenUsd of 300
• Market B has a longTokenUsd of 505 and a shortTokenUsd of 500
• A virtual inventory is comprised of Market A and Market B, with an aggregate longTokenUsd of 705 and shortTokenUsd of 800
• Bob shifts 20% of the Market A marketToken supply to Market B, 40 longTokenUsd and 60 shortTokenUsd are shifted
• During the withdrawal the virtual inventory diff goes from 705 - 800 = -95 to 665 - 740 = -75
• During the deposit the MarketB diff goes from 505 - 500 = 5 to 545 - 560 = -15, while the virtual inventory diff goes from 665 - 740 = -75 to 705 - 800 = -95
• The net virtual inventory diff stays the same from the start of the shift to the end of the shift, however the user receives increased negative impact because the deposit creates a larger imbalance in the virtual inventory than in Market B. In this scenario the user is not causing any imbalance to the virtual inventory and should therefore not be negatively impacted by the virtual inventory diff during deposit.

## Recommendation
Consider ignoring price impact from the virtual inventory when shifting between two markets that are in the same virtual inventory, as this action will never cause a further imbalance in the virtual inventory. A more complete alternative would be to consider the net virtual inventory diff created by an entire shift action, this way the virtual inventory diff created by uiFees and other potential balance changes can be accounted for.
