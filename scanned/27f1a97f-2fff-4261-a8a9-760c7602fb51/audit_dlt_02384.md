# [?] NST Simple Swap - Unverified contract, wrong approval

## Summary
Severity: Unknown
Chain: Polygon
Component: NST
Published: 2023-06-02
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-06/NST_exp.sol
Type: defi-exploit-poc

## Details
Lost: $40k
References:
- https://twitter.com/eugenioclrc
- https://polygonscan.com/tx/0xa1f2377fc6c24d7cd9ca084cafec29e5d5c8442a10aae4e7e304a4fbf548be6d
- https://openchain.xyz/trace/polygon/0xa1f2377fc6c24d7cd9ca084cafec29e5d5c8442a10aae4e7e304a4fbf548be6d

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.17;

import "forge-std/Test.sol";
import "./../interface.sol";

// REKT - NST Simple Swap
// Write up Author
// https://twitter.com/eugenioclrc
// Reported on https://discord.com/channels/1100129537603407972/1100129538056396870/1114142216923926528
// @TX
// https://polygonscan.com/tx/0xa1f2377fc6c24d7cd9ca084cafec29e5d5c8442a10aae4e7e304a4fbf548be6d
// https://openchain.xyz/trace/polygon/0xa1f2377fc6c24d7cd9ca084cafec29e5d5c8442a10aae4e7e304a4fbf548be6d
// @Summary
// Milktech is a software company that explores Polygon web3 technologies and recently ventured into
// tokens and token payments. They created a token called NST, which maintains a constant price based
// on USD. Several contracts were developed, with the main one being the swap contract. This contract
// facilitates a straightforward exchange between two tokens: NST (the internal company token) and USDT,
// ensuring a consistent price ratio. NST is an ERC-20 token with an additional role called the Minter,
// allowing specific addresses to mint new tokens. Only the owner of the contract can assign this
// role. The swap contract is ownable and features two primary functions: buyNST, which takes USDT as input,
// and sellNST, which takes NST as input. Additionally, the contract includes the ability to pause trading
// between the tokens. While the token itself was verified, the swap contract was not.

// Exploit Address: https://polygonscan.com/address/0x3bb7a0f2fe88aba35408c64f588345481490fe93
// Attacker Address: https://polygonscan.com/address/0xcb3585f3e09f0238a3f61838502590a23f15bb5b

contract NstExploitTest is Test {
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    IERC20 usdt = IERC20(0xc2132D05D31c914a87C6611C10748AEb04B58e8F);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-06/NST_exp.sol_
