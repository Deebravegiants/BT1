# [?] NFT Auction Marketplace - Double-settlement / delist refund

## Summary
Severity: Unknown
Chain: BNB Chain
Component: NFTAuctionMarketplace
Published: 2026-07-19
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/NFTAuctionMarketplace_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~2.2 BNB

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// BSC NFT Auction Marketplace -- settle-then-cancel double payout, drains the escrow pool.
// ~2.173 BNB (~$4.06k) net profit to the attacker; marketplace's entire escrowed BNB balance
// (2.2176 BNB, ~$4.15k) is drained to zero in this one tx.
//
// Root cause: the marketplace lets a listing be both settled (buyNow -> completeAuction, which
// pays the seller from the sent value) AND cancelled (delist, which refunds the same escrowed
// BNB back out of the contract's pooled balance) without completeAuction ever clearing the
// sale's paid/bid state. The attacker -- acting as both seller and buyer of a throwaway,
// self-minted NFT -- lists it, buys it (paying themselves from flash-loaned BNB), then
// immediately delists the same listing. delist re-pays the ~2.2176 BNB listing price a second
// time out of the contract's escrow pool, which is funded by OTHER users' pending
// listings/bids -- so the "refund" is actually drained from other victims' escrowed funds.
//
// Victim (marketplace proxy, unverified impl): 0x46c958a169b9f2688e126080c4ec422956621e09
// Attacker: 0xeaaf475db34fb66f098e51cbf0eeeff76f496974
// Exploit tx: 0x79dbf5d676c1f1d89cabc046743746b828fc0fa4ed70854c8b77335cd1c194df (BNB Chain)
//
// This was a CREATE tx (`to` is empty). The entire attack -- mint NFT, list, buyNow/
// completeAuction, flash-loan (Moolah/Lista WBNB) to fund the buy side, delist/double-refund,
// unwind the flash loan, forward leftover BNB -- runs inside the constructor of a one-shot
// factory contract, which internally deploys its own throwaway ERC721 and seller/buyer helper
// contracts via nested CREATEs. No attacker address is hardcoded in the creation bytecode (it
// only bakes in WBNB / USDT / PancakeRouter / the flash-loan pool / the marketplace address as
// immutables), so profit is forwarded dynamically to tx.origin.
//
// PoC strategy: fork one block before the exploit tx (state has the marketplace's real,
// other-users'-funded escrow balance of 2.2176 BNB), prank the attacker as both tx.origin and
// msg.sender, and deploy the EXACT on-chain creation bytecode via raw CREATE. The constructor
// replays the whole attack exactly as it happened on-chain.
//
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/NFTAuctionMarketplace_exp.sol_
