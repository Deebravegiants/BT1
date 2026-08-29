# [?] WiseLending03 exploit (2024-01)

## Summary
Severity: Unknown
Chain: Ethereum
Component: WiseLending03
Published: 2024-01
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-01/WiseLending03_exp.sol
Type: defi-exploit-poc

## Details
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : ~464K USD$
// Attacker : https://etherscan.io/address/0xb90cf1d740b206b6d80854bc525e609dc42b45dc
// Attack Contract : https://etherscan.io/address/0x91c49cc7fbfe8f70aceeb075952cd64817f9d82c
// Vulnerable Contract : https://etherscan.io/address/0x37e49bf3749513a02fa535f0cbc383796e8107e4
// Attack Tx :https://etherscan.io/tx/0x04e16a79ff928db2fa88619cdd045cdfc7979a61d836c9c9e585b3d6f6d8bc31

// @Info
// Vulnerable Contract Code : https://etherscan.io/address/0x37e49bf3749513a02fa535f0cbc383796e8107e4

// @Analysis
// Twitter : https://twitter.com/danielvf/status/1746303616778981402

interface IWiseLending {
    function depositExactAmount(uint256 _nftId, address _poolToken, uint256 _amount) external returns (uint256);

    function withdrawExactShares(uint256 _nftId, address _poolToken, uint256 _shares) external returns (uint256);

    function withdrawExactAmount(
        uint256 _nftId,
        address _poolToken,
        uint256 _withdrawAmount
    ) external returns (uint256);

    function getPositionLendingShares(uint256 _nftId, address _poolToken) external view returns (uint256);

    function getTotalPool(
        address _poolToken
    ) external view returns (uint256);

    function mintPosition() external returns (uint256);

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-01/WiseLending03_exp.sol_
