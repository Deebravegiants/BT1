# [M] Manager can steal up to 10% of the Vault's

## Summary
Severity: Medium
Contest weight: 0.4629
Dataset id: 22917
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The manager of a Vault can use the 1Inch protocol to swap tokens, but some checks prevent the manager from taking too much slippage on those swaps. However, the slippage checker currently allows the manager to steal up to 10% of the Vault's funds daily. When a Vault's manager wants to perform a swap using 1Inch, the contract guard OneInchV6Guard makes some checks to ensure that the manager doesn't steal any funds in the swapping process. One of those checks is done by calling the contract SlippageAccumulator, which calculates the slippage accumulated of that Vault's swaps and reverts the transaction if the accumulated slippage is above some maximum value. Here's the main snippet that checks that the slippage isn't too high:  
s/utils/SlippageAccumulator.sol#L94-L101  
```solidity
if (dstAmount < srcAmount) {
    uint128 newSlippage = srcAmount.sub(dstAmount).mul(SCALING_FACTOR).div(srcAmount).toUint128();
    uint128 newCumulativeSlippage = (
        uint256(newSlippage).add(getCumulativeSlippageImpact(swapData.poolManagerLogic))
    ).toUint128();
    require(newCumulativeSlippage < maxCumulativeSlippage, "slippage impact exceeded");
}
```
In the SlippageAccumulator contract, there are two key values set by the dHEDGE admins that determine if a swap is valid based on the slippage:  
1. maxCumulativeSlippage: This is the maximum cumulative trade slippage within a period.  
2. decayTime: This is the decay time for the accumulated slippage. E.g. If a swap has 5% slippage, it will accumulate until the decay time has passed. Currently, the deployed SlippageAccumulator contract has the following values for the mentioned variables:  
1. maxCumulativeSlippage: 10%  
2. decayTime: 1 day  
With these values, a manager of a Vault can take a maximum of 10% of slippage on all swaps in a Vault every 24 hours. This means that each day, the manager can make a swap on the Vault allowing 10% of slippage at most. With this configuration, a manager can self-sandwich a Vault's swap to extract up to 10% of the funds used for the swap. The attack sequence would look as follows:  
1. [Frontrun] The manager uses his address to take a flash loan and make a huge swap in some Uniswap pool to unbalance it.  
2. The manager uses all the Vault's funds to make a swap in the same uniswap pool allowing 10% of slippage.  
3. [Backrun] The manager uses the funds from the first transaction to reverse the swap in the pool, pocketing the 10% slippage taken by the Vault.  
4. The manager returns the flash loan with the profits.  
*All these steps will happen in a bundle so that the attack is executed in the same block. With this sequence, the manager can steal up to 10% of the Vault's funds in a single block, and this attack can be repeated every 24 hours. This means that in a week, a manager can steal up to 65.13% of the Vault's funds. This issue breaks a restriction stated in the README: Manager or trader under any circumstances should not be able to take out depositors funds put in the vaults they manage. The Vault's manager can steal up to 10% of the Vault's funds daily, 65.13% weekly. This attack doesn't need any external conditions so I think it warrants high severity.

## Recommendation
To mitigate this issue I believe the best option is to create a commit-reveal scheme for swaps. This will allow some time for the Vault's users to decide if the incoming swap may be malicious or not, allowing them to exit the Vault if necessary.
