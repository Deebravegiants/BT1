# [H] If there's enough balance in feeToken prior to the swap, fees are charged early and ETH remains stuck

## Summary
Severity: High
Contest weight: 0.3185
Dataset id: 22818
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If there's enough balance in feeToken prior to the swaps, fee will actually be charged from the ETH Even if the feeToken is the outputToken, the contract will attempt to charge fees prior to the swaps. (succeeded, feesCharged) = tryToChargeFees( feesTokenAddress, computableFeeAmount, feeRateBps, feeReceiver, receivingUser, false, false ); if (succeeded) { if (swapOps.length > 0) { require(swapOps[0].amountIn > feesCharged, "Maradona: cannot subtract fee from input swap"); swapOps[0].amountIn -= feesCharged; } else { require(bridgeOp.amountIn > feesCharged, "Maradona: cannot subtract fee from input bridge"); bridgeOp.amountIn -= feesCharged; } } The problem is that if for some reason there's enough balance of said feeToken prior to the swap, the fees will be charged. While this is not immediately a problem, if we look right after the tryToChargeFees function, we'll see that if it has succeeded, swapOps[0].amountIn will be decreased. This amount of ETH will then remain within the contract and can be skimmed by any user at any time. 1. User wishes to swap 1 ETH for DAI. Fee is 1%. 2. Attacker front-runs transaction and sends 0.01 DAI to the contract. 3. tryToChargeFees executes before the swap. Since the amount to execute on is computableFeeAmount, fee is calculated as 0.01 DAI. Since the contract has enough DAI, it sends the DAI now. 4. Since tryToChargeFees has executed, swapOps[0].amountIn will be decreased by 0.01 ETH. This 0.01 ETH will remain within the contract 5. The attacker can then skim the 0.01 ETH. Loss of funds

## Recommendation
if fee token is output token, do not try to charge fees prior to swap
