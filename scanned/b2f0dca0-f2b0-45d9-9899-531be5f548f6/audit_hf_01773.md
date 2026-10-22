# [M] ADL can result in unwrapped ETH as output which is not handled

## Summary
Severity: Medium
Contest weight: 0.4337
Dataset id: 9796
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Based on the docs and GMX V2 code, output token from ADL order can be unwrapped ETH which is not handled in the current implementation.
From <https://github.com/gmx-io/gmx-synthetics?tab=readme-ov-file#integration-notes>:

Accounts may receive ETH for ADLs / liquidations, if the account cannot receive ETH then WETH would be sent instead

In AdlUtils::createOrder() (reference), we can see that shouldUnwrapNativeToken is set to true, which will result in sending the native token to the position account later in transferOut() (reference). Additionally, since GmxProxy implements a receive() functionality, it can receive ETH instead of WETH.

The following snippet in GmxProxy.sol aims to handle ADL scenario and send funds to PerpetualVault, but it does not account the scenario mentioned above.

```solidity
else if (msg.sender == address(adlHandler)) {
      uint256 sizeInUsd = dataStore.getUint(keccak256(abi.encode(positionKey, SIZEINUSD)));
      if (eventData.uintItems.items[0].value > 0) {
        IERC20(eventData.addressItems.items[0].value).safeTransfer(perpVault, eventData.uintItems.items[0].value);
      }
      if (eventData.uintItems.items[1].value > 0) {
        IERC20(eventData.addressItems.items[1].value).safeTransfer(perpVault, eventData.uintItems.items[1].value);
      }
      if (sizeInUsd == 0) {
        IPerpetualVault(perpVault).afterLiquidationExecution();
      }
```

Stuck tokens + loss of funds for depositors.

## Recommendation
Consider checking if output token is ETH and swap it to collateral token or wrap it when received so it will be swapped like it is done before every every action.
