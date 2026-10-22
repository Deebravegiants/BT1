# [M] Collateral tokens that cannot be automatically swapped to the PnL token bypass slippage checks

## Summary
Severity: Medium
Contest weight: 0.4604
Dataset id: 19847
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Collateral tokens that cannot be automatically swapped to the PnL token, cannot have slippage applied to them, since the minOutputAmount is in units of the output token, not the secondary token.

If a user's order uses the Order.DecreasePositionSwapType.SwapCollateralTokenToPnlToken flag, it's possible for the swap to fail (e.g. because the token is paused), and in such cases, the collateral token is sent back as-is, without being converted to the PnL token. In such cases, it's not possible for the code, as it is written, to support slippage in such scenarios, because there is only one order slippage argument, minOutputAmount, and it's in units of the PnL token, not the collateral token.

A user that has a resting order open with the flag set, so that they can take profit at the appropriate time, will be forced to incur any price impact slippage present, even if they had specified a valid minOutputAmount that would otherwise have prevented the sub-optimal execution.

If the swap goes through, the secondaryOutputAmount is cleared and added to the outputAmount, but if the swap fails, it's kept as the values.output.secondaryOutputAmount:
```solidity
// File: gmx-synthetics/contracts/position/DecreasePositionCollateralUtils.sol : DecreasePositionCollateralUtils.swapWithdrawnCollateralToPnlToken()
try params.contracts.swapHandler.swap(
    ...
) returns (address tokenOut, uint256 swapOutputAmount) {
    if (tokenOut != values.output.secondaryOutputToken) {
        revert InvalidOutputToken(tokenOut, values.output.secondaryOutputToken);
    }
    // combine the values into outputToken and outputAmount
    values.output.outputToken = tokenOut;
    values.output.outputAmount = values.output.secondaryOutputAmount + swapOutputAmount;
    values.output.secondaryOutputAmount = 0;
} catch Error(string memory reason) {
    emit SwapUtils.SwapReverted(reason, "");
} catch (bytes memory reasonBytes) {
    (string memory reason, /* bool hasRevertMessage */) = ErrorUtils.getRevertMessage(reasonBytes);
    emit SwapUtils.SwapReverted(reason, reasonBytes);
}
}
return values;
}
```
cts/position/DecreasePositionCollateralUtils.sol#L383-L413

And is sent separately, with no slippage checks.

## Recommendation
Convert the USD value of secondaryOutputAmount to outputAmount, and ensure that the slippage checks against that total
