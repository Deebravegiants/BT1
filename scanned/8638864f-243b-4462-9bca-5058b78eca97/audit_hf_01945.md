# [M] Fee-on-transfer and rebase tokens.

## Summary
Severity: Medium
Contest weight: 0.2232
Dataset id: 10722
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In various parts of the codebase, assets are transferred using with the assumption that the amount transferred, is the amount received. This however isn't the case when dealing with certain tokens. i. Some charge a fee during transfers, e.g PAXG. Also important to note is that tokens like USDT also have the option to charge fees, but currently do not. ii. Some tokens, notably stETH have a 1 to 2 wei corner case, in which the amount received during a transfer is less than the amount specified. iii. Some tokens rebase, both positively and negatively, in which the holder's balance overtime increases or decreases. stETH also does this. This also includes tokens that give airdrops and the likes. These tokens have the ability to mess with the protocol's accounting if in use. This is because the transfer functions aren't optimized to handle them, and as a result can lead to situations in which the pools' asset balance will be way less than the amount expected and tracked. Here, the protocol will incur extra costs to cover for these situations. Also, the tokens received from airdrops and positive rebases can be lost forever as there's no way to retrieve them.  
The following are the functions affected.  
NablaPortal.sol - swapExactTokensForEth #L234, swapExactTokensForTokens #L293  
GenericPool.sol - _processDeposit #L96, _processWithdrawal #L118  
BackstopPoolCore.sol - _redeemSwapPoolShares L466,  
SawPool.sol - backstopDrain #L511, swapIntoFromRouter #L585, swapOutFromRouter #L670 #L675,  
RouterCore.sol - _executeSwap #L230 #L245,

## Recommendation
Before any token transfer, both in and out of the protocol, recommend checking the contract balance before and after, and registering the difference as the amount sent. This helps handle fee-on-transfer tokens, and the 1 wei corner cases. For the rebasing tokens and variable balances, a system of balance tracking and excess token sweep functions can be implemented to periodically skim the excess tokens from the contracts to prevent them from being lost. Alternativly, explicitely blocklisting these token types to prevent them from being made pool assets.
