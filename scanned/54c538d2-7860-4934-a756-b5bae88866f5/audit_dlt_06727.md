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

        // Set the global token's new branch chain address
        IPort(rootPortAddress).setLocalAddress(_globalAddress, _localAddress, _dstChainId);
    }
```

## Impact
In the case of concurrency, the second local token will overwrite the first local token.
Before overwriting, the first local token is still valid, if someone exchanges the first local token, and waits until after overwriting, then the first local token will be invalidated, and the user will lose the corresponding token.

## Proof of Concept
The following code demonstrates that with layerzero asynchronous and due to `_setLocalToken()` error checking
may cause the second localToken to overwrite the first localToken
the layerzero call is simplified

add to CoreRootBridgeAgentTest.t.sol
```solidity
    function testAddGlobalTokenOverride() public {
        //1. new global token
        GasParams memory gasParams = GasParams(0, 0);
        arbitrumCoreRouter.addLocalToken(address(arbAssetToken), gasParams);
        newGlobalAddress = RootPort(rootPort).getLocalTokenFromUnderlying(address(arbAssetToken), rootChainId);
        console2.log("New Global Token Address: ", newGlobalAddress);

        //2.1 new first local token
        gasParams = GasParams(1 ether, 1 ether);        
        GasParams[] memory remoteGas = new GasParams[](2);
        remoteGas[0] = GasParams(0.0001 ether, 0.00005 ether);
        remoteGas[1] = GasParams(0.0001 ether, 0.00005 ether);
        bytes memory data = abi.encode(ftmCoreBridgeAgentAddress, newGlobalAddress, ftmChainId,remoteGas);
        bytes memory packedData = abi.encodePacked(bytes1(0x01), data);
        encodeCallNoDeposit(
            payable(ftmCoreBridgeAgentAddress),
            payable(address(coreBridgeAgent)),
            chainNonce[ftmChainId]++,
            packedData,
            gasParams,
            ftmChainId
        );
        //2.2 new second local token

        data = abi.encode(ftmCoreBridgeAgentAddress, newGlobalAddress, ftmChainId,remoteGas);
        packedData = abi.encodePacked(bytes1(0x01), data);
        encodeCallNoDeposit(
            payable(ftmCoreBridgeAgentAddress),
            payable(address(coreBridgeAgent)),
            chainNonce[ftmChainId]++,
            packedData,
            gasParams,
            ftmChainId
        );        
        //3.1 wait some time ,lz execute first local token
        address newLocalToken = address(0xFA111111);
        data = abi.encode(newGlobalAddress, newLocalToken, "UnderLocal Coin", "UL");
        packedData = abi.encodePacked(bytes1(0x03), data);
        encodeSystemCall(
            payable(ftmCoreBridgeAgentAddress),
            payable(address(coreBridgeAgent)),
            chainNonce[ftmChainId]++,
            packedData,
            gasParams,
            ftmChainId
        );
        //3.1.1 show first local token address
        address ftmLocalToken = RootPort(rootPort).getLocalTokenFromGlobal(newGlobalAddress,ftmChainId);
        console2.log("loal Token Address(first): ", ftmLocalToken);

        //3.2 wait some time ,lz execute second local token
        gasParams = GasParams(0.0001 ether, 0.00005 ether);
        newLocalToken = address(0xFA222222);
        data = abi.encode(newGlobalAddress, newLocalToken, "UnderLocal Coin", "UL");
        packedData = abi.encodePacked(bytes1(0x03), data);
        encodeSystemCall(
            payable(ftmCoreBridgeAgentAddress),
            payable(address(coreBridgeAgent)),
            chainNonce[ftmChainId]++,
            packedData,
            gasParams,
            ftmChainId
        );
        //3.2.1 show second local token address
        ftmLocalToken = RootPort(rootPort).getLocalTokenFromGlobal(newGlobalAddress,ftmChainId);
        console2.log("loal Token Address(override): ", ftmLocalToken);        
    }    
```

```console
$ forge test -vvv --match-contract CoreRootBridgeAgentTest  --match-test testAddGlobalTokenOverride

[PASS] testAddGlobalTokenOverride() (gas: 1846078)
Logs:
  New Global Token Address:  0x12Cd3f6571aF11e01137d294866C5fFd1369Bbe9
  loal Token Address(first):  0x00000000000000000000000000000000Fa111111
  loal Token Address(override):  0x00000000000000000000000000000000fA222222

```

## Recommended Mitigation
check `isGlobalToken()` replace check `isLocalToken()`
```diff
    function _setLocalToken(address _globalAddress, address _localAddress, uint16 _dstChainId) internal {
        // Verify if the token already added
-      if (IPort(rootPortAddress).isLocalToken(_localAddress, _dstChainId)) revert TokenAlreadyAdded();
+       if (IPort(rootPortAddress).isGlobalToken(_globalAddress, _dstChainId)) {
+            revert TokenAlreadyAdded();
+       }
        // Set the global token's new branch chain address
        IPort(rootPortAddress).setLocalAddress(_globalAddress, _localAddress, _dstChainId);
    }
```



## Assessed type

Context
