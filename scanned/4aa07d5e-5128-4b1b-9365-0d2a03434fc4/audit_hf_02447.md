# [M] Improved Validation on Protocol Arguments

## Summary
Severity: Medium
Contest weight: 0.4351
Dataset id: 13137
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
DeFi protocols typically have a number of system-wide parameters that can be dynamically configured on demand. The Swing Aggregator protocol is no exception. Specifically, if we examine the SwapRouter contract, it has defined a number of protocol-wide risk parameters, such as pathCount and dexCount. In the following, we show the corresponding routines that allow for their changes.
```solidity
function setPathCount(uint256 _pathCount) external onlyOwner {
    pathCount = _pathCount;
    emit PathCountSet(_pathCount);
}
function setPathSplit(uint256 _pathSplit) external onlyOwner {
    pathSplit = _pathSplit;
    emit PathSplitSet(_pathSplit);
}
function setFactories(address[] memory _factories) external onlyOwner {
    dexCount = _factories.length;
    for (uint256 i = 0; i < _factories.length; i++) {
        factories.push(_factories[i]);
    }
    emit FactoriesSet(_factories);
}
```
These parameters define various aspects of the protocol operation and maintenance and need to exercise extra care when configuring or updating them. Our analysis shows the update logic on these parameters can be improved by applying more rigorous sanity checks. Based on the current implementation, certain corner cases may lead to an undesirable consequence. For example, the above setFactories() routine needs to update dexCount as dexCount += _factories.length;, not current dexCount = _factories.length; (line 412). Note the same issue also affects another routine, i.e., SwitchRoot::setFactories().

## Recommendation
Validate any changes regarding these system-wide parameters to ensure they fall in an appropriate range.
