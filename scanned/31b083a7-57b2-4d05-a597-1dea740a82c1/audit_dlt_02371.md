# [?] ARA - Incorrect handling of permissions

## Summary
Severity: Unknown
Chain: BNB Chain
Component: ARA
Published: 2023-06-18
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-06/ARA_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$125k
References:
- https://twitter.com/BeosinAlert/status/1670638160550965248

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : ~125K USD$
// Attacker : https://bscscan.com/address/0xf84efa8a9f7e68855cf17eaac9c2f97a9d131366
// Attack Contract : https://bscscan.com/address/0x98e241bd3be918e0d927af81b430be00d86b04f9
// Vulnerable Contract : https://bscscan.com/address/0x7ba5dd9bb357afa2231446198c75bac17cefcda9
// Attack Tx : https://bscscan.com/tx/0xd87cdecd5320301bf9a985cc17f6944e7e7c1fbb471c80076ef2d031cc3023b2

// @Analysis
// https://twitter.com/BeosinAlert/status/1670638160550965248

interface IPancakeRouterV3 {
    struct ExactInputSingleParams {
        address tokenIn;
        address tokenOut;
        uint24 fee;
        address recipient;
        uint256 amountIn;
        uint256 amountOutMinimum;
        uint160 sqrtPriceLimitX96;
    }

    function exactInputSingle(
        ExactInputSingleParams memory params
    ) external payable returns (uint256 amountOut);
}

contract ARATest is Test {
    IERC20 BUSDT = IERC20(0x55d398326f99059fF775485246999027B3197955);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-06/ARA_exp.sol_
