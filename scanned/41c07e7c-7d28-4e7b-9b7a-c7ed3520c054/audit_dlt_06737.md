# [H] Impossibility to change `safeCollateralRatio`

## Summary
Severity: High
Chain: Smart contract
Component: 2023-06-lybra
Published: 2023-07-03
Source: https://github.com/code-423n4/2023-06-lybra-findings/issues/882
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-06-lybra/blob/main/contracts/lybra/configuration/LybraConfigurator.sol#L199
https://github.com/code-423n4/2023-06-lybra/blob/main/contracts/lybra/pools/base/LybraEUSDVaultBase.sol#L30
https://github.com/code-423n4/2023-06-lybra/blob/main/contracts/lybra/pools/base/LybraPeUSDVaultBase.sol#L18


# Vulnerability details

## Impact
Because of `vaultType` variable is internal `vaultType` staticcall to vaults from the configurator will revert, so it makes it impossible to change `safeCollateralRatio`. It may be critical when market conditions will change, something happens with ETH. 

## Proof of Concept
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Test.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {GovernanceTimelock} from "@lybra/governance/GovernanceTimelock.sol";
import {LybraStETHDepositVault} from "@lybra/pools/LybraStETHVault.sol";
import {Configurator} from "@lybra/configuration/LybraConfigurator.sol";
import {mockEtherPriceOracle} from "@mocks/mockEtherPriceOracle.sol";
import {mockCurve} from "@mocks/mockCurve.sol";

/* remappings used
@lybra=contracts/lybra/
@mocks=contracts/mocks/
 */
contract LybraV2SafeCollateral is Test {

    GovernanceTimelock govTimeLock;
    mockEtherPriceOracle oracle;
    mockCurve curve;
    Configurator configurator;
    LybraStETHDepositVault stETHVault;
    address owner = address(7);
    // admins && executers of GovernanceTimelock
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-06-lybra-findings/issues/882_
