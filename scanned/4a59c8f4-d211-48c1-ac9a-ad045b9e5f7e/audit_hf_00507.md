# [H] H-01 | tradeRatio Rounded In Wrong Direction

## Summary
Severity: High
Contest weight: 0.2404
Dataset id: 1965
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The recommendation of [H-03](https://www.notion.so/H-03-1348bda5828c810ba6bbe5baf4a7ed02?pvs=21) is to round up the trade ratio when going towards the long direction as a short. However, the fix implemented is the opposite - the trade ratio is being rounded down if isLongDirection and rounded up otherwise. Since the problem is not solved, the insolvency issue still exists. Currently, tradeRatioD18 is used to compute both closePnL and vEthAmount/borrowedVEth. Foil's goal should always be to maximize borrowedVEth and minimize closePnL and vEthAmount. Because of this, different rounding directions should be used depending on what's being calculated.

## Recommendation
The end goal should be to maximize the borrowedVEth and minimize the vEthAmount and closePnL. To accomplish this, you can have two different tradeRatios - one rounded down and one rounded up. You will also have three different vEthToZero. The first one will be to calculate the closePnL and you will use the tradeRatio that’s rounded down if the position is a long, otherwise use the rounded up one. The second vEthToZero will always use the tradeRatio that’s rounded down and the third vEthToZero will always use the tradeRatio that’s rounded up. Next, you will also have two different vEthFromZero for each vEthToZero. Finally, in the if/else statement where you set borrowedVEth and vEthAmount you will choose the appropriate vEthFromZero. For the if case you should use the vEthFromZero which absolute value is bigger to maximize borrow and for the else case you should use the vEthFromZero which absolute value is smaller to minimize the credited vETH.
