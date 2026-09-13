# [M] _handleExecuteTransaction may not working correctly on fee-on-transfer tokens. Moreover, if it is failed, fund may be locked forever.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-06-connext
Published: 2022-06-19
Source: https://github.com/code-423n4/2022-06-connext-findings/issues/196
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-06-connext/blob/4dd6149748b635f95460d4c3924c7e3fb6716967/contracts/contracts/core/connext/facets/BridgeFacet.sol#L856-L877
https://github.com/code-423n4/2022-06-connext/blob/4dd6149748b635f95460d4c3924c7e3fb6716967/contracts/contracts/core/connext/helpers/Executor.sol#L142-L144
https://github.com/code-423n4/2022-06-connext/blob/4dd6149748b635f95460d4c3924c7e3fb6716967/contracts/contracts/core/connext/helpers/Executor.sol#L160-L166
https://github.com/code-423n4/2022-06-connext/blob/4dd6149748b635f95460d4c3924c7e3fb6716967/contracts/contracts/core/connext/helpers/Executor.sol#L194-L213


# Vulnerability details

## Impact
_handleExecuteTransaction may not working correctly on fee-on-transfer tokens. As duplicated fee is applied to fee on transfer token when executing a arbitrary call message passing request. Moreover, the Executor contract increase allowance on that token for that target contract in **full amount without any fee**, this may open a vulnerability to steal dust fund in the contract

Moreover, failure is trying to send **full amount without any fee** which is not possible because fee is already applied one time for example 100 Safemoon -> 90 Safemoon but trying to transfer 100 safemoon to _recovery address. Obviously not possible since we only have 90 Safemoon. This will revert and always revert causing loss of fund in all case of fee-on-transfer tokens.

## Proof of Concept

A message to transfer 100 Safemoon with some contract call payload has been submitted by a relayer to _handleExecuteTransaction function on BridgeFacet these lines hit.

```
      // execute calldata w/funds
      AssetLogic.transferAssetFromContract(_asset, address(s.executor), _amount);
      (bool success, bytes memory returnData) = s.executor.execute(
        IExecutor.ExecutorArgs(
          _transferId,
          _amount,
          _args.params.to,
          _args.params.recovery,
          _asset,
          _reconciled
            ? LibCrossDomainProperty.formatDomainAndSenderBytes(_args.params.originDomain, _args.originSender)
            : LibCrossDomainProperty.EMPTY_BYTES,
          _args.params.callData
        )
      );
```

Noticed that 100 Safemoon is transferred to executor before contract execution. Now executor has 90 Safemoon due to 10% fee on transfer.

```
    if (!isNative) {
      SafeERC20Upgradeable.safeIncreaseAllowance(IERC20Upgradeable(_args.assetId), _args.to, _args.amount);
    }
```

Next, we increase allowance of target contract to transfer 100 more Safemoon.

```
    // Try to execute the callData
    // the low level call will return `false` if its execution reverts
    (success, returnData) = ExcessivelySafeCall.excessivelySafeCall(
      _args.to,
      gas,
      isNative ? _args.amount : 0,
      MAX_COPY,
      _args.callData
    );
```

After that, it call target contract

```
    // Try to execute the callData
    // the low level call will return `false` if its execution reverts
    (success, returnData) = ExcessivelySafeCall.excessivelySafeCall(
      _args.to,
      gas,
      isNative ? _args.amount : 0,
      MAX_COPY,
      _args.callData
    );
```

Target contract tried to pull 100 Safemoon from Executor but now Executor only has 90 Safemoon, so contract call failed. Moving on to the failure handle.

```
  function _handleFailure(
    bool isNative,
    bool hasIncreased,
    address _assetId,
    address payable _to,
    address payable _recovery,
    uint256 _amount
  ) private {
    if (!isNative) {
      // Decrease allowance
      if (hasIncreased) {
        SafeERC20Upgradeable.safeDecreaseAllowance(IERC20Upgradeable(_assetId), _to, _amount);
      }
      // Transfer funds
      SafeERC20Upgradeable.safeTransfer(IERC20Upgradeable(_assetId), _recovery, _amount);
    } else {
      // Transfer funds
      AddressUpgradeable.sendValue(_recovery, _amount);
    }
  }
```

isNative = false because of Safemoon

Trying to transfer 100 Safemoon to _recovery while only having 90 Safemoon in the contract. Thus failure handle is reverted.

## Tools Used
Manual

## Recommended Mitigation Steps
You should approve one step only. Avoid an extra token transfer.
