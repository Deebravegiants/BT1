# [H] Chain operator can DOS entire cluster during upgrade block, potentially stealing ETH from other chains

## Summary
Severity: High
Contest weight: 0.6734
Dataset id: 11091
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Interop Network Upgrade (as well as other OP hard forks that include L2 contract changes), the upgrade block is organized as follows:
1) L1 Attributes Transaction calling setL1BlockValuesEcotone.
2) User deposits from L1.
3) Network upgrade transactions.
It is required that the block has sufficient gas for all of these transactions, because they are all deposit transactions and therefore must be included in the block. If this is not the case, we will get an ErrGasLimitReached. This will cause a crash of all op-node and op-program instances, halting the chain and making fault proofs impossible to prove.
At a minimum, this will DoS the entire cluster. Depending how interop fault proofs are implemented, it also may create the opportunity for the malicious chain operator to propose a malicious root that cannot be disputed. In this case, they could create a root that include a withdrawal of all ETH in the SharedLockbox, stealing funds from the other chains.
Is it possible for a single chain operator to create this out of gas situation? We can see in SystemConfig.sol, the setGasLimit() function is callable by the chain operator. It requires that they set the gas limit to at least the minimum:
```solidity
function minimumGasLimit() public view returns (uint64) {
    return uint64(_resourceConfig.maxResourceLimit) + uint64(_resourceConfig.systemTxMaxGas);
}
```
However, as we can see, this minimum only takes into account the L1 attributes transaction (systemTxMaxGas) and user deposits (maxResourceLimit). It is therefore possible to reduce the gas limit down to the minimum, use all the possible gas for user deposits, and force the network upgrade transaction to run out of gas.

## Proof of Concept
• Let's imagine a chain has 1mm allocated for the system transaction and 20mm for user deposits.
• The total of all the upgrade transactions is 5mm gas.
• Some time before the upgrade block, the chain operator lowers the gas limit to the minimum (21mm).
• At the upgrade block, they submit a 20mm gas transaction through the bridge.
• As the upgrade block executes, it will use some portion of the 1mm for the system transaction, all 20mm for the user deposits, and not have sufficient gas left in the block for the network upgrade transactions.
• The result is that the chain halts, with op-node and op-program unable to perform derivation.

## Recommendation
Ensure an additional buffer is added between the L2 gas limit and systemTxMaxGas + maxResourceLimit. Ensure all network upgrade transactions use an amount of gas that is less than this buffer.
