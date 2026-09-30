# [M] Proper Paths Update in setPaths()

## Summary
Severity: Medium
Contest weight: 0.4614
Dataset id: 11701
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
DeFi protocols typically have a number of system-wide parameters that can be dynamically configured on demand. The AVaultBase protocol is no exception. Specifically, if we examine the AVaultBase contract, it has defined a number of protocol-wide risk parameters, such as buyBackRate and withdrawFeeFactor. In the following, we show the corresponding routines that allow for their changes.
```solidity
function setPaths(
    address[] memory _earnedToWethPath,
    address[] memory _wethToAVAPath,
    address[] memory _earnedToToken0Path,
    address[] memory _earnedToToken1Path,
    address[] memory _token0ToEarnedPath,
    address[] memory _token1ToEarnedPath
) external virtual onlyOwner {
    require(earnedToWethPath[0] == _earnedToWethPath[0] &&
        earnedToWethPath[earnedToWethPath.length - 1] == _earnedToWethPath[_earnedToWethPath.length - 1], "earnedToWethPath");
    require(wethToAVAPath[0] == _wethToAVAPath[0] &&
        wethToAVAPath[wethToAVAPath.length - 1] == _wethToAVAPath[_wethToAVAPath.length - 1], "wethToAVAPath");
    require(earnedToToken0Path[0] == _earnedToToken0Path[0] &&
        earnedToToken0Path[earnedToToken0Path.length - 1] == _earnedToToken0Path[_earnedToToken0Path.length - 1], "earnedToToken0Path");
    require(earnedToToken1Path[0] == _earnedToToken1Path[0] &&
        earnedToToken1Path[earnedToToken1Path.length - 1] == _earnedToToken1Path[_earnedToToken1Path.length - 1], "earnedToToken1Path");
    require(token0ToEarnedPath[0] == _token0ToEarnedPath[0] &&
        token0ToEarnedPath[token0ToEarnedPath.length - 1] == _token0ToEarnedPath[_token0ToEarnedPath.length - 1], "token0ToEarnedPath");
    require(token1ToEarnedPath[0] == _token1ToEarnedPath[0] &&
        token1ToEarnedPath[token1ToEarnedPath.length - 1] == _token1ToEarnedPath[_token1ToEarnedPath.length - 1], "token1ToEarnedPath");
    emit PathsUpdated();
}
```
These parameters define various aspects of the protocol operation and maintenance and need to exercise extra care when configuring or updating them. Our analysis shows the update logic on these parameters can be improved by applying more rigorous sanity checks. Based on the current implementation, certain setter functions do not properly update these parameters. To elaborate, we show above the setPaths() routine, which is designed to configure various swap paths for token conversion. However, it comes to our attention the current setter only performs the necessary validation on the given parameters and does not properly save these configurations!

## Recommendation
Validate any changes regarding these system-wide parameters and properly save them in the storage. If necessary, also consider emitting relevant events for their changes.
