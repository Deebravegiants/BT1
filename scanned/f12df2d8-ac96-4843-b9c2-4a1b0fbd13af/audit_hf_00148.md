# [M] reputation risks with `updateSolution`

## Summary
Severity: Medium
Contest weight: 0.4167
Dataset id: 663
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`GovDev.sol` has a function `updateSolution` to upgrade parts of the contract via the Diamond construction. Via `updateSolution`, any functionality can be changed and all the funds can be accessed/rugged. Even if this is well intended the project could still be called out resulting in a reputation risk, see for [example](https://twitter.com/RugDocIO/status/1411732108029181960).

Note: there is a function `transferGovDev` which can be used to disable the `updateSolution`

```solidity
function updateSolution(IDiamondCut.FacetCut[] memory _diamondCut, address _init, bytes memory _calldata) external override {
    require(msg.sender == LibDiamond.contractOwner(), 'NOT_DEV');
    return LibDiamond.diamondCut(_diamondCut, _init, _calldata);
}
```

Recommend applying extra safeguards for example to limit the time period where `updateSolution` can be used.

Fair point, although we are not anonymous, we still want to mitigate this risk.

I’m thinking something like this
  * update is pushed, everyone can review the code changes
  * 14 days of waiting, people are able to get their funds out
  * update is executed.

Downside is that it doesn’t allow us to fix potential critical issues fast.

## Recommendation
No recommendation
