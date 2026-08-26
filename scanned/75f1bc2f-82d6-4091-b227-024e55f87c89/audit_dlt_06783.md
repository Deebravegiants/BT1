# [M] Vultisig should be burnable

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-06-vultisig
Published: 2024-07-29
Source: https://github.com/code-423n4/2024-06-vultisig-findings/issues/224
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-06-vultisig/blob/cb72b1e9053c02a58d874ff376359a83dc3f0742/hardhat-vultisig/contracts/Vultisig.sol#L1-L25


# Vulnerability details

The Vultisig token, as described in its documentation, is expected to include a burnable feature. However, the current implementation of the Vultisig token contract lacks the necessary functions to support token burning. This report identifies the impact of this missing functionality and provides a recommended solution to implement the burn feature. The vultisig stated that they forgot to add this functionality.
## Impact

**Non-compliance with Documentation:** Users and developers relying on the documentation will expect burn functionality, leading to confusion and potential loss of trust when they find it missing.
## Proof of concept 

As you can see from the code below function for burning is missing, consider adding it to the code. 

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {IApproveAndCallReceiver} from "./interfaces/IApproveAndCallReceiver.sol";

/**
 * @title ERC20 based Vultisig token contract
 */
contract Vultisig is ERC20, Ownable {
    constructor() ERC20("Vultisig Token", "VULT") {
        _mint(_msgSender(), 100_000_000 * 1e18);
    }

    function approveAndCall(
        address spender,
        uint256 amount,
        bytes calldata extraData
    ) external returns (bool) {
        // Approve the spender to spend the tokens
        _approve(msg.sender, spender, amount);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-06-vultisig-findings/issues/224_
