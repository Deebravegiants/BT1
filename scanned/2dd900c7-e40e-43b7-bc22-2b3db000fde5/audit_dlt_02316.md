# [?] - LaunchZone - Access Control

## Summary
Severity: Unknown
Chain: BNB Chain
Component: LaunchZone
Published: 2023-02-27
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/LaunchZone_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$320,000
References:
- https://blog.verichains.io/p/analyzing-the-lz-token-hack
- https://twitter.com/immunefi/status/1630210901360951296
- https://bscscan.com/tx/0xaee8ef10ac816834cd7026ec34f35bdde568191fe2fa67724fcf2739e48c3cae
- https://twitter.com/launchzoneann/status/1631538253424918528

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Test.sol";

// analysis
// https://blog.verichains.io/p/analyzing-the-lz-token-hack
// https://twitter.com/immunefi/status/1630210901360951296
// https://bscscan.com/tx/0xaee8ef10ac816834cd7026ec34f35bdde568191fe2fa67724fcf2739e48c3cae exploit tx

// reponse
// https://twitter.com/launchzoneann/status/1631538253424918528

// contracts to study
// https://bscscan.com/address/0x0ccee62efec983f3ec4bad3247153009fb483551 proxy for implementation (verified)
// https://bscscan.com/address/0x6D8981847Eb3cc2234179d0F0e72F6b6b2421a01 implementation (unverified)
// https://bscscan.com/address/0x1c2b102f22c08694eee5b1f45e7973b6eaca3e92  attacker contract

interface UniRouterLike {
    function swap(uint256 amount0Out, uint256 amount1Out, address to, bytes calldata data) external;

    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);

    function getAmountsOut(
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/LaunchZone_exp.sol_
