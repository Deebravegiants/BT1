# [C] C-08 | vETH Proﬁt In Long Pos Deleted On Close

## Summary
Severity: Critical
Contest weight: 0.2261
Dataset id: 22051
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a trader owns a long position that made a good amount of proﬁt and the trader decreases the position so that the full loan is repaid the system will: • calculate the excess vETH after fully repaying the borrowedVEth amount • set the borrowedVEth to 0 • save the excess vETH as vEthAmount in the position by calling updateBalance This is unusual as normally a long position has a vGasAmount amount > 0 and a borrowedVEth amount > 0, but the vEthAmount is usually 0. This state is problematic when closing the long position as the ﬂow of closing the position looks like the following: • Swap the positions vGasAmount to vETH • Increase the depositedCollateralAmount by the amount of vETH received from the swap • Set the borrowedVEth to 0 • Call the resetBalance function to set the currentTokenAmount, vEthAmount & vGasAmount to 0 Therefore the trader's proﬁt saved in the vEthAmount variable is deleted.

## Recommendation
Increase the positions depositedCollateralAmount instead of the vEthAmount when decreasing a long position with proﬁt > the borrowed vETH amount.
