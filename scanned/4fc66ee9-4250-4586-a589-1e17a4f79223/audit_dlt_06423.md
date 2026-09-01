# [M] Inconsistency in Handling WETH in `eth::most::receiveRequest`

## Summary
Severity: Medium
Chain: Smart contract
Component: Most--Aleph-Zero-Bridge
Published: 2024-03-21
Source: https://github.com/hats-finance/Most--Aleph-Zero-Bridge-0xab7c1d45ae21e7133574746b2985c58e0ae2e61d/issues/34
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x82d2682c8143b7687373b20de9007b5e79b82735a356e972857eb3f4a6381a11
**Severity:** medium

**Description:**
**Description**\
In the `eth::most::receiveRequest` function, there's a check `if (_destTokenAddress == wethAddress)`. The issue here is that using `wethAddress` to differentiate between tokens and ETH will cause issues.

**Scenario**

Consider a contract, Contract B, that only works with WETH and doesn't accept ETH. Here's what might happen:

1. Contract B sends some WETH to the bridge contract.
2. Later on, Contract B wants to retrieve the WETH.
3. However, since in `receiveRequest` WETH tokens are converted to ETH, the transfer fails

**Impact**  
Users might expect to receive WETH but will actually receive ETH instead. This could lead to unexpected behavior, especially for contracts that only accept tokens and not ETH. This would result in a loss of funds for users, although recoverable by the owner.


**POC**
- cd eth
- npm install --save-dev @nomicfoundation/hardhat-foundry
- npm install --save-dev @nomicfoundation/hardhat-toolbox
- import this in your Hardhat config: require ("@nomicfoundation/hardhat-foundry");
- npx hardhat init-foundry
- forge test --fork-url "RPC Link" --fork-block-number "19481680" --match-path test/poc.t.sol -vvvvv

```solidity
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../contracts/Most.sol";
import "forge-std/console2.sol";
import "../contracts/Token.sol";
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Most--Aleph-Zero-Bridge-0xab7c1d45ae21e7133574746b2985c58e0ae2e61d/issues/34_
