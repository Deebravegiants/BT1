# [?] SocketGateway - Lack of calldata validation

## Summary
Severity: Unknown
Chain: Ethereum
Component: SocketGateway
Published: 2024-01-12
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-01/SocketGateway_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~3.3Million $

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "../basetest.sol";
import "./../interface.sol";

interface ISocketGateway {
    function executeRoute(uint32 routeId, bytes calldata routeData) external payable returns (bytes memory);
}

interface ISocketVulnRoute {
    function performAction(
        address fromToken,
        address toToken,
        uint256 amount,
        address receiverAddress,
        bytes32 metadata,
        bytes calldata swapExtraData
    ) external payable returns (uint256);
}

// @KeyInfo - Total Lost : ~3.3M US$
// Attacker : https://etherscan.io/address/0x50DF5a2217588772471B84aDBbe4194A2Ed39066
// Attack Contract : https://etherscan.io/address/0xf2D5951bB0A4d14BdcC37b66f919f9A1009C05d1
// Created Attack Contract: https://etherscan.io/address/0xd2bc9A9c2C39B8693ED4B2b72469032E87ED7F4a
// Vulnerable Contract : https://etherscan.io/address/0x3a23F943181408EAC424116Af7b7790c94Cb97a5 (the faulty route is vulnerable not the gateway itself)
// Attack Tx : https://etherscan.io/tx/0xc6c3331fa8c2d30e1ef208424c08c039a89e510df2fb6ae31e5aa40722e28fd6

// @Info
// Vulnerable Contract Code : https://etherscan.io/address/0xCC5fDA5e3cA925bd0bb428C8b2669496eE43067e#code

// @Analysis
// Post-mortem :https://twitter.com/BeosinAlert/status/1747450173675196674
// Twitter Guy : https://twitter.com/peckshield/status/1747353782004900274

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-01/SocketGateway_exp.sol_
