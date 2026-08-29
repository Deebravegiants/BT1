# [?] WiseLending - Bad HealthFactor Check

## Summary
Severity: Unknown
Chain: Ethereum
Component: WiseLending02
Published: 2024-01-12
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-01/WiseLending02_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~464K

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

import {Test, console} from "forge-std/Test.sol";
import {IERC20} from "./../interface.sol";

// @KeyInfo - Total Lost : ~464K USD$
// Attacker : https://etherscan.io/address/0xb90cf1d740b206b6d80854bc525e609dc42b45dc
// Attack Contract : https://etherscan.io/address/0x91c49cc7fbfe8f70aceeb075952cd64817f9d82c
// Vulnerable Contract : https://etherscan.io/address/0x37e49bf3749513a02fa535f0cbc383796e8107e4
// Attack Tx :https://etherscan.io/tx/0x04e16a79ff928db2fa88619cdd045cdfc7979a61d836c9c9e585b3d6f6d8bc31

// @Info
// Vulnerable Contract Code : https://etherscan.io/address/0x37e49bf3749513a02fa535f0cbc383796e8107e4

// @Analysis
// Twitter alert by Exvul : https://twitter.com/EXVULSEC/status/1746138811862577515
// Twitter alert by Peckshield: https://twitter.com/peckshield/status/1745907642118123774

contract WiseLendingTest is Test {
    IWiseLending public wiseLending = IWiseLending(payable(0x37e49bf3749513A02FA535F0CbC383796E8107E4));

    NFTManager public nft = NFTManager(0x32E0A7F7C4b1A19594d25bD9b63EBA912b1a5f61);

    uint256 blockNumber = 18_983_652;

    // PLP-stETH-Dec2025
    address poolToken = 0xB40b073d7E47986D3A45Ca7Fd30772C25A2AD57f;

    address pendleLPT = 0xC374f7eC85F8C7DE3207a10bB1978bA104bdA3B2;

    address other;

    address wsteth = 0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0;

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-01/WiseLending02_exp.sol_
