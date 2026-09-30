# [M] \[M03\] Re-entrancy possibilities

## Summary
Severity: Medium
Source: https://github.com/mcdexio/mai-protocol-v2/blob/4b198083ec4ae2d6851e101fc44ea333eaa3cd92/contracts/perpetual/Collateral.sol#L51
Type: audit-issue

## Details
[Solidity recommends the usage of the Check-Effects-Interaction Pattern](https://solidity.readthedocs.io/en/latest/security-considerations.html#use-the-checks-effects-interactions-pattern) to avoid potential security issues, such as reentrancy. However, there are several examples of interactions preceding effects:

* In the `deposit` function of the `Collateral` contract, [collateral is retrieved](https://github.com/mcdexio/mai-protocol-v2/blob/4b198083ec4ae2d6851e101fc44ea333eaa3cd92/contracts/perpetual/Collateral.sol#L51) before [the user balance is updated and an event is emitted](https://github.com/mcdexio/mai-protocol-v2/blob/4b198083ec4ae2d6851e101fc44ea333eaa3cd92/contracts/perpetual/Collateral.sol#L54-L56).
* In the `_withdraw` function of the `Collateral` contract, [collateral is sent](https://github.com/mcdexio/mai-protocol-v2/blob/4b198083ec4ae2d6851e101fc44ea333eaa3cd92/contracts/perpetual/Collateral.sol#L81-L85) before the [event is emitted](https://github.com/mcdexio/mai-protocol-v2/blob/4b198083ec4ae2d6851e101fc44ea333eaa3cd92/contracts/perpetual/Collateral.sol#L86)
* The same pattern occurs in the [depositToInsuranceFund](https://github.com/mcdexio/mai-protocol-v2/blob/4b198083ec4ae2d6851e101fc44ea333eaa3cd92/contracts/perpetual/Perpetual.sol#L180), [depositEtherToInsuranceFund](https://github.com/mcdexio/mai-protocol-v2/blob/4b198083ec4ae2d6851e101fc44ea333eaa3cd92/contracts/perpetual/Perpetual.sol#L192) and [withdrawFromInsuranceFund](https://github.com/mcdexio/mai-protocol-v2/blob/4b198083ec4ae2d6851e101fc44ea333eaa3cd92/contracts/perpetual/Perpetual.sol#L204) functions of the `Perpetual` contract.

It should be noted that even when a correctly implemented ERC20 contract is used for collateral, incoming and outgoing transfers could execute arbitrary code if the contract is also ERC777 compliant. These re-entrancy opportunities are unlikely to corrupt the internal state of the system, but they would effect the order and contents of emitted events, which could confuse external clients about the state of the system. Consider always following the “Check-Effects-Interactions” pattern.

**Update:** _Fixed. The [ReentrancyGuard](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/utils/ReentrancyGuard.sol) contract is now used to protect those functions._
