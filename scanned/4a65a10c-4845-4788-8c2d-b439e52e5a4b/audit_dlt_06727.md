# [M] addGlobalToken() localAdress could be overwritten

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-09-maia
Published: 2023-10-06
Source: https://github.com/code-423n4/2023-09-maia-findings/issues/610
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-09-maia/blob/f5ba4de628836b2a29f9b5fff59499690008c463/src/CoreRootRouter.sol#L483


# Vulnerability details

## Vulnerability details
`CoreBranchRouter.addGlobalToken()` is used to set the local token of chains.
when `CoreBranchRouter.addGlobalToken(_dstChainId = ftm)` , will execute follow step:
1. [root]CoreRootRouter._addGlobalToken()
      - 1.1 check isGlobalAddress(_globalAddress)
      - 1.2 check not isGlobalToken(_globalAddress, _dstChainId)
2.  [branch]CoreBranchRouter._receiveAddGlobalToken()
      - 2.1 [remote:ftm]  CoreBranchRouter._receiveAddGlobalToken()
           - 2.1.1 New Local Token address
3. [root] CoreRootRouter._setLocalToken()
      - 3.1 check not isLocalToken(new Local token)
      - 3.2 rootPort.setLocalAddress(globalGlobal,new Local token, fmtChainId)
             
Call sequence [root]->[branch]->[root], with asynchronous calls via layerzero.
Since it is asynchronous, in the case of concurrency, the check in step [1.2] is invalid because step [3.2] is executed after a certain amount of time.

Consider the following scenarios
1. alice execute `addGlobalToken(ftm)`  through Steps [1] and [2], and generate `alice_LocalTokenAddress = 0x01
2. bob executes `addGlobalToken(ftm)` through Steps [1] and [2], and generate `bob_LocalTokenAddress = 0x02` at the same time. 
3. after a while layerzero executes alice's request, will pass step 3.1 , because alice_LocalTokenAddress is new
4. after a while layerzero executes bob's request, will pass step 3.1 , because bob_LocalTokenAddress is new

So `bob_LocalTokenAddress` will override `alice_LocalTokenAddress`.

The main problem here is that the check in step [3.1] is wrong, because the local token is a regenerated address, so isLocalToken() is always flase.
It should be checking `isGlobalToken(_globalAddress, _dstChainId))`

```solidity
    function _setLocalToken(address _globalAddress, address _localAddress, uint16 _dstChainId) internal {
        // Verify if the token already added
@>      if (IPort(rootPortAddress).isLocalToken(_localAddress, _dstChainId)) revert TokenAlreadyAdded();
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-09-maia-findings/issues/610_
