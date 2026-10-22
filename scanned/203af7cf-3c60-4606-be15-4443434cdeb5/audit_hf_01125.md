# [H] User can call liquidate

## Summary
Severity: High
Contest weight: 0.5411
Dataset id: 4596
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious user is able to steal all collateral of an unhealthy position in `PARMinerV2.sol`. The code for the `liquidate()` function is written so that the following steps are followed:

* User calls `PARMinerV2.liquidate()`
* PARMinerV2 performs the liquidation with `_a.parallel().core().liquidatePartial()`
* PARMinerV2 receives the liquidated collateral
* An arbitrary router function is called to swap the collateral to PAR
* Finally, `PARMinerV2.liquidate()` checks that PARMinerV2’s PAR balance is higher than the balance at the beginning of the function call.

The exploit occurs with the arbitrary router call. The malicious user is able to supply the `dexTxnData` parameter which dictates the function call to the router. If the user supplied a function such as UniswapV2Router’s `swapExactTokenForETH()`, then control flow will be given to the user, allowing them to perform the exploit.

Note: The Mimo developers have stated that the routers used by the protocol will be DEX Aggregators such as 1inch and Paraswap, but this submission will be referring to UniswapV2Router for simplicity. It can be assumed that the dex aggregators currently allow swapping tokens for ETH.

Continuing the exploit, once the attacker has gained control due to the ETH transfer, they are able to swap the ETH for PAR. Finally, they deposit the PAR with `PARMinerV2.deposit()`. This will cause the final check of `liquidate()` to pass because PARMinerV2’s PAR balance will be larger than the start of the liquidation call.

The attacker is able to steal all collateral from every unhealthy position that they liquidate. In the most extreme case, the attacker is able to open their own risky positions with the hope that the position becomes unhealthy. They will borrow the PAR and then liquidate themselves to take back the collateral. Thus effectively stealing PAR.

## Proof of Concept
Steps for exploit:

* Attacker monitors unhealthy positions. Finds a position to liquidate.
* Attacker calls `PARMinerV2.liquidate()`
* Position liquidated. Collateral transferred back to `PARMinerV2`
* In the `liquidate()` function, attacker supplies bytes for `UniswapV2Router.swapExactTokensForETH(uint amountIn, uint amountOutMin, address[] calldata path, address to, uint deadline)`. For `to`, they supply the attacker contract.
* `swapExactTokensForETH()` firstly swaps the collateral for ETH and then transfers the ETH to the user with `TransferHelper.safeTransferETH(to, amounts[amounts.length - 1]);`
* `TransferHelper.safeTransferETH()` contains a call to the receiver via `(bool success, ) = to.call{value: value}(new bytes(0));`
* Therefore, the attacker contract will indeed gain control of execution.

The attacker contract will then perform the following steps:

* Swap the received ETH to PAR.
* Deposit the PAR in `PARMinerV2`
* Withdraw the deposited PAR.

## Recommendation
The arbitrary call to the router contracts is risky because of the various functions that they can contain. Perhaps a solution is to only allow certain calls such as swapping tokens to tokens, not ETH. This would require frequently updated knowledge of the router’s functions, though would be beneficial for security.

Also, adding a check that the `_totalStake` variable has not increased during the liquidation call will mitigate the risk of the attacker depositing the PAR to increase the contract’s balance. The attacker would have no option but to transfer the PAR to PARMinerV2 as is intended.

We believe in theory this attack is actually possible, but highly unlikely to happen. It also begs the question of whether it’s really worth it for an attacker to do this because they could just call VaultsCore.liquidate() themselves (for example with a flashloan) and stake all the PAR they profit that way directly.

We misunderstood this exploit wrong and we confirm it. Basically, if the attacker was liquidating a 10,000 PAR position, he could potentially end up with a 10,000 PAR stake + liquidation profits. Our previous understanding was that he could only end up with the profits.

At the very least we’ll implement a check that `totalStake` hasn’t changed, we will carefully consider if more changes are needed.
