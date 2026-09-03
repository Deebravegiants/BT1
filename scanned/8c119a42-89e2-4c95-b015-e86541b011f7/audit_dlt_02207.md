# [?] Audius - Storage Collision & Malicious Proposal

## Summary
Severity: Unknown
Chain: Ethereum
Component: Audius
Published: 2022-07-23
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-07/Audius_exp.sol
Type: defi-exploit-poc

## Details
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : 704 ETH (~ 1,080,000 US$)
// Attacker : 0xa0c7bd318d69424603cbf91e9969870f21b8ab4c
// AttackContract : 0xbdbb5945f252bc3466a319cdcc3ee8056bf2e569
// Tx1 initialize + ProposalSubmitted + Staked :  https://etherscan.io/tx/0xfefd829e246002a8fd061eede7501bccb6e244a9aacea0ebceaecef5d877a984
// Tx2 submitVote : https://etherscan.io/tx/0x3c09c6306b67737227edc24c663462d870e7c2bf39e9ab66877a980c900dd5d5
// Tx3 evaluateProposal : https://etherscan.io/tx/0x4227bca8ed4b8915c7eec0e14ad3748a88c4371d4176e716e8007249b9980dc9
// Tx4 AUDIO/WETH Swap : https://etherscan.io/tx/0x82fc23992c7433fffad0e28a1b8d11211dc4377de83e88088d79f24f4a3f28b3

// @Info
// Governance Contract (Proxy) : https://etherscan.io/address/0x4deca517d6817b6510798b7328f2314d3003abac#code
// Governance Contract (Logic) : https://etherscan.io/address/0x1c91af03a390b4c619b444425b3119e553b5b44b#code
// Stacking Contract (Proxy) : https://etherscan.io/address/0xe6d97b2099f142513be7a2a068be040656ae4591#code
// Stacking Contract (Logic) : https://etherscan.io/address/0xea10fd3536fce6a5d40d55c790b96df33b26702f#code
// DelegateManagerV2 (Proxy) : https://etherscan.io/address/0x4d7968ebfd390d5e7926cb3587c39eff2f9fb225#code
// DelegateManagerV2 (Logic) : https://etherscan.io/address/0xf24aeab628493f82742db68596b532ab8a141057#code
// UniswapV2 Router 2 : https://etherscan.io/address/0x7a250d5630b4cf539739df2c5dacb4c659f2488d#code

// @NewsTrack
// Official Announcement : https://twitter.com/AudiusProject/status/1551000725169180672
// Official Post-Mortem : https://blog.audius.co/article/audius-governance-takeover-post-mortem-7-23-22
// SunSec : https://twitter.com/1nf0s3cpt/status/1551050841146400768
// Abmedia News : https://abmedia.io/20220724-audius-hacked-by-mal-governance-proposal
// Beosin Alert : https://twitter.com/BeosinAlert/status/1551041795735408641
// CertiK Alert : https://twitter.com/CertiKAlert/status/1551020421532770305
// MistTrack : https://twitter.com/MistTrack_io/status/1551204726661734400

CheatCodes constant cheat = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
address constant attacker = 0xa0c7BD318D69424603CBf91e9969870F21B8ab4c;
address constant AUDIO = 0x18aAA7115705e8be94bfFEBDE57Af9BFc265B998;
address payable constant uniswap = payable(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D);
address constant governance = 0x4DEcA517D6817B6510798b7328F2314d3003AbAC;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-07/Audius_exp.sol_
