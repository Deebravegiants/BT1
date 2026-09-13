# [M] Omni X incident: Decentralized NFT financialization protocol Omni X has been attacked and stolen funds have been transferred to Tornado.cash. The m

## Summary
Severity: Medium
Target: Omni X
Loss: 1,300 ETH
Attack method: Reentrancy Attack
Published: 2022-07-10
Source: https://www.theblock.co/post/156800/hacker-drains-1-4-million-worth-of-eth-from-nft-lender-omni
Type: slowmist-incident

## Details
Decentralized NFT financialization protocol Omni X has been attacked and stolen funds have been transferred to Tornado.cash. The main reason for this attack is that the burn function will call the callback function externally to cause the reentrancy problem, and the liquidation function uses the old vars value for judgment, resulting in the user's status identification even after reentrancy and then borrowing. Being set as unborrowed results in no repayments.
