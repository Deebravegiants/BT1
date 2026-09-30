# [M] M-01 | NFT Marketplace Bidding Bait-And-Switch

## Summary
Severity: Medium
Contest weight: 0.2477
Dataset id: 21303
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Whenever a mirror ERC721 token is transferred, minted, or burned through ERC20 transfers, the order in which the mirror tokens are taken from the holder is LIFO (last in first out). This behavior can be abused in certain circumstance by a malicious actor to steal user funds when interacting with NFT marketplaces. The exact situation happens when a user that has a bid on a mirror NFT also sells a unit or more of base tokens from the same wallet. In that case, a malicious holder of the mirror NFT can make a profit and leave the user without the rare NFT. Attack scenario using the live [Asterix](https://opensea.io/collection/asterixlabs) collection as an example: Bob has one of the rarest NFTs, [1960](https://opensea.io/assets/ethereum/0x0000000000c26fabfe894d13233d5ec73f61cc72/1960) and waits for people to bid on it. At this point, Alice bids on it for 1.2938 WETH. The floor for the collection is 0.674 ETH and buying an NFT by buying the base tokens from the [liquidity pool](https://www.dextools.io/app/en/ether/pair-explorer/0x68e4af213c49f320175116bff189c9ca452ce29c?t=1714341972227) is 0.5671 ETH. Alice has another NFT, lowest rarity, and sells by selling a unit of base tokens. Since the collection is on Ethereum, the base swap transaction can be seen in the mempool. Bob sees the base unit sell and front-runs it with accepting Alice’s bid. Alice gets the rare 1960 ID and pays 1.2938 WETH, but immediately loses it as it was the last in and the base unit sell burns it, marking her a loss of 1.2938 - 0.5671 ETH. Bob quickly initiates several cycled mints/burns to reclaim the rare NFT. Even if Bob fails to reclaim it, Alice still suffered a loss of the rare NFT. The above case can also happen unintentionally, when a user bid is accepted exactly in the same block as him selling base tokens equivalent to a NFT, having the same financial loss.

## Recommendation
Consider modifying the synchronization logic to that of a FIFO (first in first out) instead of LIFO. Meaning that the first NFT to be minted to the wallet is also the first to leave it. Otherwise consider clearly documenting this risk for integrators.
