# [C] Bridge Token Would Be Locked and Cannot Bridge to Native Token

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description
If the bridge token B of a native token A is already deployed and `confirmDeployment` is called on the other layer and `setDeployed` sets  A's `nativeToBridgedToken`  value to `DEPLOYED_STATUS`. The bridge token B cannot bridge to native token A in `completeBridging` function, because A's `nativeToBridgedToken`  value is not `NATIVE_STATUS`, as a result the native token won't be transferred to the receiver. User's bridge token will be locked in the original layer  
 
#### Examples

**contracts/TokenBridge.sol:L217-L229**
```solidity
if (nativeMappingValue == NATIVE_STATUS) {
  // Token is native on the local chain
  IERC20(_nativeToken).safeTransfer(_recipient, _amount);
} else {
  bridgedToken = nativeMappingValue;
  if (nativeMappingValue == EMPTY) {
    // New token
    bridgedToken = deployBridgedToken(_nativeToken, _tokenMetadata);
    bridgedToNativeToken[bridgedToken] = _nativeToken;
    nativeToBridgedToken[_nativeToken] = bridgedToken;
  }
  BridgedToken(bridgedToken).mint(_recipient, _amount);
}
```


**contracts/TokenBridge.sol:L272-L279**
```solidity
function setDeployed(address[] memory _nativeTokens) external onlyMessagingService fromRemoteTokenBridge {
  address nativeToken;
  for (uint256 i; i < _nativeTokens.length; i++) {
    nativeToken = _nativeTokens[i];
    nativeToBridgedToken[_nativeTokens[i]] = DEPLOYED_STATUS;
    emit TokenDeployed(_nativeTokens[i]);
  }
}
```


#### Recommendation

Add an condition `nativeMappingValue` = `DEPLOYED_STATUS` for native token transfer in `confirmDeployment`
 ```
if (nativeMappingValue == NATIVE_STATUS || nativeMappingValue == DEPLOYED_STATUS) {
    IERC20(_nativeToken).safeTransfer(_recipient, _amount);
```
<!-- Supply advice on how to best fix the problem. -->
