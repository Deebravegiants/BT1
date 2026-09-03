# [H] `executeWithdraw` may be blocked if any of the users are blacklisted from the `baseToken`

## Summary
Severity: High
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1426
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/accountingManager/AccountingManager.sol#L428


# Vulnerability details

https://github.com/d-xo/weird-erc20#tokens-with-blocklists

> Some tokens (e.g. `USDC`, `USDT`) have a contract level admin controlled address blocklist. If an address is blocked, then transfers to and from that address are forbidden.

> Malicious or compromised token owners can trap funds in a contract by adding the contract address to the blocklist. This could potentially be the result of regulatory action against the contract itself, against a single user of the contract (e.g. a Uniswap LP), or could also be a part of an extortion attempt against users of the blocked contract.

If a user whose address has been blocklisted is added to a `withdrawQueue` inside the `AccountingManager` contract, all other users that are in that same queue will not be able to withdraw, as the `executeWithdraw` function will revert when it tries to do `[baseToken.safeTransfer](https://github.com/code-423n4/2024-04-noya/blob/main/contracts/accountingManager/AccountingManager.sol#L428)` call on the blocklisted address.

## Impact

A user who has been blocklisted can be added to a `withdrawQueue` to DoS the call of the `executeWithdraw` function, effectively preventing all other user that are in that same queue from withdrawing, locking their assets inside the protocol.

## Proof of Concept

When `baseToken` has blocklisting functionality, and any user in the withdrawal queue is in the blocklist, it prevents all other users from making withdrawals.

_Place the following test in [testFoundry/BlacklistableTokenPOC.t.sol](https://github.com/code-423n4/2024-04-noya/tree/9c79b332eff82011dcfa1e8fd51bad805159d758/testFoundry) and run it with the command `forge test --mt testBlacklistableERC20`_

```solidity
// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.20;

import "@openzeppelin/contracts-5.0/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts-5.0/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts-5.0/token/ERC20/ERC20.sol";
import "./utils/testStarter.sol";
import "./utils/resources/OptimismAddresses.sol";
import { AaveConnector, BaseConnectorCP } from "contracts/connectors/AaveConnector.sol";

contract BlacklistERC20 is ERC20 {
    mapping(address => bool) private blacklisted;
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1426_
