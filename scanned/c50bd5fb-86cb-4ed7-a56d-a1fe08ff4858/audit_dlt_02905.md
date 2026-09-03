# [?] Venus THE - BorrowBehalf + Donation Attack

## Summary
Severity: Unknown
Chain: EVM
Component: Venus_THE
Published: 2026-03-15
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-03/Venus_THE_exp.sol
Type: defi-exploit-poc

## Details
Lost: 913,858.263360521396654198 CAKE + 1,972.530910582753621682 WBNB

```solidity
// SPDX-License-Identifier: UNLICENSED
// @KeyInfo - Total Lost : still held as raw CAKE + WBNB at the end of the tx
// Attacker : https://bscscan.com/address/0x43C743e316F40d4511762EEdf6f6D484F67b2F82
// Attack Contract : https://bscscan.com/address/0x737bc98F1D34E19539C074B8Ad1169d5d45dA619
// Attack Tx : https://bscscan.com/tx/0x4f477e941c12bbf32a58dc12db7bb0cb4d31d41ff25b2457e6af3c15d7f5663f

// Trace-driven state changing path:
// 1. Drain THE from six EOAs that had pre-approved the future attack-contract address.
// 2. Donate those THE directly into Venus vTHE to inflate the market's exchange rate / collateral value.
// 3. Use Venus borrowBehalf to borrow USDC onto a victim's debt while sending the cash to the attacker.
// 4. Mint vUSDC with the stolen USDC, enter that market, then borrow THE and donate it back into vTHE.
// 5. Reuse the victim's now-overvalued vTHE collateral to borrow CAKE and WBNB on the victim's behalf.

pragma solidity ^0.8.15;

import "forge-std/Test.sol";

interface IERC20Minimal {
    function balanceOf(
        address account
    ) external view returns (uint256);
    function transfer(
        address to,
        uint256 amount
    ) external returns (bool);
    function transferFrom(
        address from,
        address to,
        uint256 amount
    ) external returns (bool);
    function approve(
        address spender,
        uint256 amount
    ) external returns (bool);
}
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-03/Venus_THE_exp.sol_
