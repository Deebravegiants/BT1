# [M] `LibDiamond.diamondCut

## Summary
Severity: Medium
Contest weight: 0.7454
Dataset id: 11172
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[LibDiamond.sol#L100-L103](https://github.com/code-423n4/2022-06-connext/blob/main/contracts/contracts/core/connext/libraries/LibDiamond.sol#L100-L103)  
[LibDiamond.sol#L71-L79](https://github.com/code-423n4/2022-06-connext/blob/main/contracts/contracts/core/connext/libraries/LibDiamond.sol#L71-L79)  
[LibDiamond.sol#L83-L90](https://github.com/code-423n4/2022-06-connext/blob/main/contracts/contracts/core/connext/libraries/LibDiamond.sol#L83-L90)  

Normally, `diamondStorage().acceptanceTimes[keccak256(abi.encode(_diamondCut))]` will be set in `LibDiamond.proposeDiamondCut()`. Then in `LibDiamond.diamondCut()`, it checks that `diamondStorage().acceptanceTimes[keccak256(abi.encode(_diamondCut))] < block.timestamp`.

However, `LibDiamond.rescindDiamondCut()` will set `diamondStorage().acceptanceTimes[keccak256(abi.encode(_diamondCut))]` to 0. Which can easily pass the check in `diamondCut()`. But `rescindDiamondCut` should rescind `_diamondCut`. In conclusion, using `rescindDiamondCut()` can easily bypass the delay time.

Moreover, if `proposeDiamondCut()` has never been called, the check for delay time is always passed.

## Proof of Concept
`diamondStorage().acceptanceTimes[keccak256(abi.encode(_diamondCut))]` will be set in `LibDiamond.proposeDiamondCut()`  
[LibDiamond.sol#L71-L79](https://github.com/code-423n4/2022-06-connext/blob/main/contracts/contracts/core/connext/libraries/LibDiamond.sol#L71-L79)  

```solidity
function proposeDiamondCut(
  IDiamondCut.FacetCut[] memory _diamondCut,
  address _init,
  bytes memory _calldata
) internal {
  uint256 acceptance = block.timestamp + _delay;
  diamondStorage().acceptanceTimes[keccak256(abi.encode(_diamondCut))] = acceptance;
  emit DiamondCutProposed(_diamondCut, _init, _calldata, acceptance);
}
```

Then in `LibDiamond.diamondCut()`, it checks that `diamondStorage().acceptanceTimes[keccak256(abi.encode(_diamondCut))] < block.timestamp`  
[LibDiamond.sol#L100-L103](https://github.com/code-423n4/2022-06-connext/blob/main/contracts/contracts/core/connext/libraries/LibDiamond.sol#L100-L103)  

```solidity
function diamondCut(
  IDiamondCut.FacetCut[] memory _diamondCut,
  address _init,
  bytes memory _calldata
) internal {
  require(
    diamondStorage().acceptanceTimes[keccak256(abi.encode(_diamondCut))] < block.timestamp,
    "LibDiamond: delay not elapsed"
  );
  …
}
```

However, `LibDiamond.rescindDiamondCut()` will set `diamondStorage().acceptanceTimes[keccak256(abi.encode(_diamondCut))]` to 0. Which can easily pass the check in `diamondCut()`  
[LibDiamond.sol#L83-L90](https://github.com/code-423n4/2022-06-connext/blob/main/contracts/contracts/core/connext/libraries/LibDiamond.sol#L83-L90%3E)  

```solidity
function rescindDiamondCut(
  IDiamondCut.FacetCut[] memory _diamondCut,
  address _init,
  bytes memory _calldata
) internal {
  diamondStorage().acceptanceTimes[keccak256(abi.encode(_diamondCut))] = 0;
  emit DiamondCutRescinded(_diamondCut, _init, _calldata);
}
```

`diamondStorage().acceptanceTimes[keccak256(abi.encode(_diamondCut))] = 0 < block.timestamp`

## Recommendation
Add another check in `diamondCut`
    
```solidity
function diamondCut(
  IDiamondCut.FacetCut[] memory _diamondCut,
  address _init,
  bytes memory _calldata
) internal {
  require(
    diamondStorage().acceptanceTimes[keccak256(abi.encode(_diamondCut))] < block.timestamp && diamondStorage().acceptanceTimes[keccak256(abi.encode(_diamondCut))] != 0,
    "LibDiamond: delay not elapsed"
  );
  …
}
```

**[jakekidd (Connext) resolved](https://github.com/code-423n4/2022-06-connext-findings/issues/215#issuecomment-1166765584):**

Resolved by [connext/nxtp@cde1353](https://github.com/connext/nxtp/commit/cde1353c27e8c4deebc1c808a37a8b57884e3c43)

I believe this issue to be valid but of `medium` severity as it requires a malicious or compromised governance. This issue would allow the protocol’s admin to propose and execute any arbitrary data within the same transaction.
