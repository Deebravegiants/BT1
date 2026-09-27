# [M] APE incident: According to a report by Twitter user Will Sheehan, the arbitrage bot took out more than 6w APE Coins (worth $8 each) through flas

## Summary
Severity: Medium
Target: APE
Loss: $ 500,000
Attack method: Airdrop Mechanism Vulnerability
Published: 2022-03-17
Source: https://twitter.com/wilburforce_/status/1504437189979119622
Type: slowmist-incident

## Details
According to a report by Twitter user Will Sheehan, the arbitrage bot took out more than 6w APE Coins (worth $8 each) through flash loans. After analysis, it was found that this was related to a loophole in the airdrop mechanism of APE Coin. Specifically, whether APE Coin can be airdropped depends on whether a user holds the instantaneous state of BYAC NFT, and this instantaneous state attacker can manipulate by borrowing a flash loan and then redeeming to obtain BYAC NFT. The attacker first borrows BYAC Token through flash loan, and then redeems to obtain BYAC NFT. Then use these NFTs to claim the airdropped APE, and finally use the BYAC NFT mint to obtain BYAC Token to return the flash loan.
