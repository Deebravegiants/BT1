# [C] TradableMarginHandler: margin account withdraw message will revert on the sideVault

## Summary
Severity: Critical
Contest weight: 0.7435
Dataset id: 16121
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users are unable to withdraw their tokens on a sideVault.
On the TradableMarginHandler contract, function withdrawalValidation(), line 263 states:
```solidity
sendMessage(dstVault, abi.encodePacked("mw", user, selectedToken.token, amount));
```
Here, since abi.encodePacked is used, instead of abi.encode, this message cannot be decoded by the side vault. Since the side vault is on a different chain, the call to withdrawalValidation() will be successful, but the call to _nonblockingLzReceive() on the side Vault will always revert.
Take a look at the following proof of concept:
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract test_encodePacked {
    function test() external {
        address user = address(10);
        uint256 amount = 100;
        bytes memory payload = abi.encodePacked("mw", user, amount);
        (string memory messageType) = abi.decode(payload, (string)); // This line always reverts
    }
}
```

## Recommendation
use abi.encode
