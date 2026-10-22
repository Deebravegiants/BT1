# [M] M-09 | Rounding In Favor Of User

## Summary
Severity: Medium
Contest weight: 0.1406
Dataset id: 22065
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are instances where the protocol rounds in favor of the user. Even though these rounding errors are small, a user withdrawing even a slight amount more than they are entitled to can lead to insufficient funds to pay out the last withdrawer. In the settle function of Position.sol: self.borrowedVEth rounds down: self.borrowedVEth = (self.borrowedVGas * settlementPriceD18) / 1e18; Then in the next line self.borrowedVEth is subtracted as part of the user's collateral calculation: self.depositedCollateralAmount = self.vEthAmount - self.borrowedVEth; Since borrowedVEth is lower than the exact value, then this makes the user's collateral slightly higher than it should be. In _afterSettlementSwapExactOut, this equation calculates the amountIn a user needs to get a certain amount out. Since it rounds down, the user can put in less than their required amount: requiredAmountInVGas = amountOutVEth.divDecimal(epoch.settlementPriceD18);

## Recommendation
Consider substituting a division function which rounds in the instances where rounding down would be in favor of the user.
