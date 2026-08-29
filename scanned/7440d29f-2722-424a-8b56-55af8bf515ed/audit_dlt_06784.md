# [M] The ````_matcho()```` is not implemented properly

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-04-rubicon
Published: 2023-04-13
Source: https://github.com/code-423n4/2023-04-rubicon-findings/issues/1243
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-04-rubicon/blob/511636d889742296a54392875a35e4c0c4727bb7/contracts/RubiconMarket.sol#L1313


# Vulnerability details

## Impact
The ````_matcho()```` function is not implemented properly, it might revert while the taking amount is greater than the best offer's amount, leads to order matching failure.

## Proof of Concept
The following test script shows how to trigger the issue.
```solidity
pragma solidity ^0.8.0;

import "../../contracts/compound-v2-fork/WhitePaperInterestRateModel.sol";
import "../../contracts/compound-v2-fork/ComptrollerInterface.sol";
import "../../contracts/compound-v2-fork/CErc20Delegator.sol";
import "../../contracts/compound-v2-fork/CErc20Delegate.sol";
import "../../contracts/compound-v2-fork/Comptroller.sol";
import "../../contracts/utilities/MarketAidFactory.sol";
import "../../contracts/periphery/TokenWithFaucet.sol";
import "../../contracts/utilities/MarketAid.sol";
import "../../contracts/periphery/WETH9.sol";
import "../../contracts/RubiconMarket.sol";
import "forge-std/Test.sol";

/// @notice proxy isn't used here
contract MatchingOfferNotWorking is Test {
  //========================CONSTANTS========================
  address public owner;
  address FEE_TO = 0x0000000000000000000000000000000000000FEE;
  address taker = address(0x1234);
  address maker = address(0x5678);
  // core contracts
  RubiconMarket market;
  // test tokens
  TokenWithFaucet RUBI;
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-04-rubicon-findings/issues/1243_
