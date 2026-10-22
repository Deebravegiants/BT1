# [M] `address.call{value:x}`

## Summary
Severity: Medium
Contest weight: 0.4129
Dataset id: 17031
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When withdrawing and refund ETH, the contract uses Solidity’s `transfer()` function.

Using Solidity’s `transfer()` function has some notable shortcomings when the withdrawer is a smart contract, which can render ETH deposits impossible to withdraw. Specifically, the withdrawal will inevitably fail when:

  * The withdrawer smart contract does not implement a payable fallback function.
  * The withdrawer smart contract implements a payable fallback function which uses more than 2300 gas units.
  * The withdrawer smart contract implements a payable fallback function which needs less than 2300 gas units but is called through a proxy that raises the call’s gas usage above 2300.

Risks of reentrancy stemming from the use of this function can be mitigated by tightly following the “Check-Effects-Interactions” pattern and using OpenZeppelin Contract’s ReentrancyGuard contract.

## Proof of Concept
```solidity
// Line-of-Credit/contracts/utils/LineLib.sol
payable(receiver).transfer(amount);
```

## Recommendation
Using low-level `call.value(amount)` with the corresponding result check or using the OpenZeppelin `Address.sendValue` is advised, [reference](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/Address.sol#L60).
