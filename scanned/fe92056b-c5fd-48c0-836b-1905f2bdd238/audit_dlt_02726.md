# [?] Moonhacker - improper input validation

## Summary
Severity: Unknown
Chain: Optimism
Component: Moonhacker
Published: 2024-12-23
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-12/Moonhacker_exp.sol
Type: defi-exploit-poc

## Details
Lost:  318.9 k

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "../basetest.sol";
import "../interface.sol";

// @KeyInfo - Total Lost :  318.9 k
// Attacker : https://optimistic.etherscan.io/address/0x36491840ebcf040413003df9fb65b6bc9a181f52
// Attack Contract1 : https://optimistic.etherscan.io/address/0x4e258f1705822c2565d54ec8795d303fdf9f768e
// Attack Contract2 : https://optimistic.etherscan.io/address/0x3a6eaaf2b1b02ceb2da4a768cfeda86cff89b287
// Vulnerable Contract : https://optimistic.etherscan.io/address/0xd9b45e2c389b6ad55dd3631abc1de6f2d2229847
// Attack Tx : https://optimistic.etherscan.io/tx/0xd12016b25d7aef681ade3dc3c9d1a1cc12f35b2c99953ff0e0ee23a59454c4fe

// @Info
// Vulnerable Contract Code : https://optimistic.etherscan.io/address/0xd9b45e2c389b6ad55dd3631abc1de6f2d2229847#code (MoonHacker.sol)
// Mtoken code : https://optimistic.etherscan.io/address/0xA9CE0A4DE55791c5792B50531b18Befc30B09dcC#code (MToken.sol)
// Mtoken docs : https://docs.moonwell.fi/moonwell/developers/mtokens/contract-interactions

// @Analysis
// On-chain transaction analysis: https://app.blocksec.com/explorer/tx/optimism/0xd12016b25d7aef681ade3dc3c9d1a1cc12f35b2c99953ff0e0ee23a59454c4fe
// Post-mortem : https://blog.solidityscan.com/moonhacker-vault-hack-analysis-ab122cb226f6
// Twitter Guy : https://x.com/quillaudits_ai/status/1871607695700296041
// Hacking God : https://x.com/CertiKAlert/status/1871347300918030409

interface IMusdc {
    function borrowBalanceCurrent(address account) external returns (uint);
    function getAccountSnapshot(address account) external returns (uint, uint, uint, uint);
}

interface IMoonhacker {
    function executeOperation(
        address token,
        uint256 amountBorrowed,
        uint256 premium,
        address initiator,
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-12/Moonhacker_exp.sol_
