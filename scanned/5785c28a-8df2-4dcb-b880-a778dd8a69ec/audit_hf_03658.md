# [M] Gasless ETH bridging from L1 to L2

## Summary
Severity: Medium
Contest weight: 0.2543
Dataset id: 19739
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can submit deposit transactions on L1 using the depositTransaction of the OptimismPortal contract. Among other parameters, the user must specify the gas limit.
The function does not enforce any minimum gas limit to pay for the submission of the transaction on L2. Therefore, it is possible to submit deposit gasless transactions (i.e., with a gas limit of zero). These gasless transactions trigger a number of interesting consequences on the system.
First, because the gas limit is set to zero, the deposit transaction won't accumulate any gas on the prevBoughtGas on L1. Therefore, they're not constrained by the MAX_RESOURCE_LIMIT.
Second, the resource and gas cost on L1 will be zero. And therefore they will never trigger the gas burning mechanism on L1. Users don't have to pay for the consumed L2 resources in advance.
Third, when the transaction is executed on L2, it will be run with a gas limit of zero. Unsurprisingly, execution will fail. This is a reasonable behavior. Although under certain circumstances, it will still allow the user to alter L2 state. In particular, if a user submits on L1 a deposit transaction with zero gas limit and positive msg.value, it will record a mint of the corresponding ETH on L2, even if the transaction fails.
Thus effectively allowing users to bridge ETH from L1 to L2 in a gasless fashion, without paying in advance for the L2 resources consumed.
must still be included. Unless we cannot produce the block at all due to the gas limit. However, these gasless deposits bypass the block gas limit, and in this aspect guarantee inclusion. Because they consume no gas at all.
Here's a real example of gasless ETH bridging. In this L1 tx, the account 0x612c calls depositTransaction with msg.value of 1 wei and gasLimit set to zero. The transaction executes successfully. Some seconds later, the corresponding L2 tx is executed. It fails, but it increases account's ETH balance on L2 by 1 wei.
I should mention that the specs do explain the behavior of failed deposits, explicitly stating that the mint on L2 will succeed and the nonce will be increased. However, it assumes the costs of the operation (even if failed) have already been paid on L1. This issue would prove the assumption incorrect.
Gasless bridging of ETH allows users to only pay for the L1 execution of their ETH deposit transactions. They allow users to spend L2-bridging resources without paying for them in advance on L1.
Also, the issue renders the expected way of bridging ETH pointless. Because the default for an ETH deposit to L2 uses a gas limit of 100000 units.

## Recommendation
Enforce on L1 a minimum gas limit that the users must pay for to successfully begin invocation on L2. I would suggest exploring the possibility to at least charge the intrinsic gas cost of the transaction on L1, so as to ensure the user is paying for the minimum gas a transaction must have to even be considered on L2.
