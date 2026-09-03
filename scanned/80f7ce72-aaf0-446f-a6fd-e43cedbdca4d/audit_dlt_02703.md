# [?] MorphoBlue - Overpriced Asset in Oracle

## Summary
Severity: Unknown
Chain: Ethereum
Component: MorphoBlue
Published: 2024-10-13
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-10/MorphoBlue_exp.sol
Type: defi-exploit-poc

## Details
Lost: $230,000

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "../basetest.sol";

// @KeyInfo - Total Lost : $230,000
// Attacker : https://etherscan.io/address/0x02DBE46169fDf6555F2A125eEe3dce49703b13f5
// Attack Contract : https://etherscan.io/address/0x4095F064B8d3c3548A3bebfd0Bbfd04750E30077
// Vulnerable Contract : https://etherscan.io/address/0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb
// Attack Tx : https://etherscan.io/tx/0x256979ae169abb7fbbbbc14188742f4b9debf48b48ad5b5207cadcc99ccb493b

// @Info
// Vulnerable Contract Code : https://etherscan.io/address/0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb#code

// @Analysis
// Post-mortem :
// Twitter Guy : https://x.com/omeragoldberg/status/1845515843787960661
// Hacking God :
pragma solidity ^0.8.0;

interface IMorphoBundler {
    error UnsafeCast();

    function MORPHO() external view returns (address);

    function ST_ETH() external view returns (address);

    function WRAPPED_NATIVE() external view returns (address);

    function WST_ETH() external view returns (address);

    function approve2(
        IAllowanceTransfer.PermitSingle memory permitSingle,
        bytes memory signature,
        bool skipRevert
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-10/MorphoBlue_exp.sol_
