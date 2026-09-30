# [M] Vultisig should be burnable

## Summary
Severity: Medium
Contest weight: 0.6189
Dataset id: 21558
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Vultisig token, as described in its documentation, is expected to include a burnable feature. However, the current implementation of the Vultisig token contract lacks the necessary functions to support token burning. This report identifies the impact of this missing functionality and provides a recommended solution to implement the burn feature. The vultisig stated that they forgot to add this functionality.

## Proof of Concept
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

        // Call the receiveApproval function on the spender contract
        IApproveAndCallReceiver(spender).receiveApproval(
            msg.sender,
            amount,
            address(this),
            extraData
        );

        return true;
    }
}
```

## Recommendation
To address this issue, the following burn functions should be added to the Vultisig contract:

  1. **Burn Function:**

     * Allows token holders to destroy a specified amount of their own tokens.
  2. **Burn From Function:**

     * Allows an account to burn tokens from another account, given that the caller has sufficient allowance.

Here is the modified contract with the added burn functionality. Something like this can be added to the `Vultisig` code:

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

        // Call the receiveApproval function on the spender contract
        IApproveAndCallReceiver(spender).receiveApproval(
            msg.sender,
            amount,
            address(this),
            extraData
        );

        return true;
    }

    function burn(uint256 amount) public {
        _burn(msg.sender, amount);
    }

    function burnFrom(address account, uint256 amount) public {
        uint256 currentAllowance = allowance(account, msg.sender);
        require(currentAllowance >= amount, "ERC20: burn amount exceeds allowance");
        _approve(account, msg.sender, currentAllowance - amount);
        _burn(account, amount);
    }
}
```
