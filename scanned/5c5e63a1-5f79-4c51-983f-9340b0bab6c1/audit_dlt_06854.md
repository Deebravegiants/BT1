# [M] Wrong `DOMAIN_TYPEHASH` definition

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-05-velodrome
Published: 2022-05-29
Source: https://github.com/code-423n4/2022-05-velodrome-findings/issues/114
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-05-velodrome/blob/7fda97c570b758bbfa7dd6724a336c43d4041740/contracts/contracts/VotingEscrow.sol#L1106
https://github.com/code-423n4/2022-05-velodrome/blob/7fda97c570b758bbfa7dd6724a336c43d4041740/contracts/contracts/VotingEscrow.sol#L1354-L1391


# Vulnerability details

## Impact

Broke the [EIP 712](https://eips.ethereum.org/EIPS/eip-712), and the `delegateBySig` function


## Proof of Concept

In the build of the `DOMAIN TYPEHASH` the `string version` is forgotten, but the `delegateBySig` function, build the `domainSeparator` with the `string version`

Some contract or dapp/backend could building the `DOMAIN_TYPEHASH` with _"rigth"_ struct(include the `version`) and try to use the `delegateBySig` function but this function will revert in the L1378 with the message `"VotingEscrow::delegateBySig: invalid signature"` because the expect `DOMAIN_TYPEHASH` in the `VotingEscrow.sol` contract was built with the _"wrong"_ struct


## Recommended Mitigation Steps

Acording the [EIP 712](https://eips.ethereum.org/EIPS/eip-712), in the [Definition of domainSeparator](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-712.md#definition-of-domainseparator):
  - _"`string version` the current major version of the signing domain. Signatures from different versions are not compatible"_

Add `string version`, to the `EIP712Domain` string, [L1106](https://github.com/code-423n4/2022-05-velodrome/blob/7fda97c570b758bbfa7dd6724a336c43d4041740/contracts/contracts/VotingEscrow.sol#L1106):
```solidity
bytes32 public constant DOMAIN_TYPEHASH = keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)");
```

## Other recommendation

Build the `domainSeparator` [L1362](https://github.com/code-423n4/2022-05-velodrome/blob/7fda97c570b758bbfa7dd6724a336c43d4041740/contracts/contracts/VotingEscrow.sol#L1362) in the constructor to save gas and clarify/clean code

1. Remove the `bytes32 public constant DOMAIN_TYPEHASH` [L1106](https://github.com/code-423n4/2022-05-velodrome/blob/7fda97c570b758bbfa7dd6724a336c43d4041740/contracts/contracts/VotingEscrow.sol#L1106)
2. Add `bytes32 private immutable DOMAIN_SEPARATOR` as a contract VAR
3. Assign the `DOMAIN_SEPARATOR` in the constructor
4. Use the `DOMAIN_SEPARATOR` in `delegateBySig` function when buil the `bytes32 digest`

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-05-velodrome-findings/issues/114_
