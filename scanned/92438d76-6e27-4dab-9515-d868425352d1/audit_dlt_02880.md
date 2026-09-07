# [?] Kame - Arbitary External Call

## Summary
Severity: Unknown
Chain: EVM
Component: Kame
Published: 2025-09-13
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-09/Kame_exp.sol
Type: defi-exploit-poc

## Details
Lost: 18167.8 USD

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "../basetest.sol";

interface IAggregationRouter {
    struct SwapParams {
        address srcToken;
        address dstToken;
        uint256 amount;
        address payable executor;
        bytes executeParams;
        bytes extraData;
    }

    function swap(
        SwapParams calldata params
    ) external payable returns (uint256 returnAmount);

    event Swapped(address srcToken, address dstToken, uint256 amount, uint256 returnAmount, bytes extraData);
}

// @KeyInfo - Total Lost : 18167.880000 USD
// Attacker : https://seiscan.io//address/0xd43d0660601e613f9097d5c75cd04ee0c19e6f65
// Attack Contract : N/A
// Vulnerable Contract : https://seiscan.io//address/0x14bb98581ac1f1a43fd148db7d7d793308dc4d80
// Attack Tx : https://seiscan.io//tx/0x6150ec6b2b1b46d1bcba0cab9c3a77b5bca218fd1cdaad1ddc7a916e4ce792ec

// @Info
// Vulnerable Contract Code : https://seiscan.io//address/0x14bb98581ac1f1a43fd148db7d7d793308dc4d80#code

// @Analysis
// Post-mortem : N/A
// Twitter Guy : https://x.com/SupremacyHQ/status/1966909841483636849
// Hacking God : N/A
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-09/Kame_exp.sol_
