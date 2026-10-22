# [M] setVoteFactor() does not change existing sup-

## Summary
Severity: Medium
Contest weight: 0.5930
Dataset id: 20247
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
AdvancedDistributor.setVoteFactor() does not change existing supply of vote tokens. If it is called before all distribution records have been initialized, there will be a skew between those who initialized before and those who initialized after. Further, if it is increased, those who initialized before will not have enough vote tokens to withdraw. Increase scenario (very bad): 1. Owner makes airdrop and sets vote factor to 1. Many people get a claim to 1000 airdrop tokens. 2. People initialize their distribution records. They are minted 1000 vote tokens. 3. Owner sets vote factor to 2 4. The airdrop tokens vest 5. No-one who already initialized their distribution record can withdraw anything because they don't have enough vote tokens. (Vote tokens are burned when executing a claim.) Decrease scenario (less bad): 1. Owner makes an airdrop for 1000 people managed by a CrosschainMerkleDistribution and sets vote factor to 1000 2. User Speedy Gonzalez calls initializeDistributionRecord() for himself 3. Owner decides to change the vote factor to 1 instead 4. All other users only get 1 voting token, but Speedy still has 1000 Increase scenario If the vote factor is increased after deploying the contract, some people will not be able to withdraw, period. It is still possible, however, for the owner of the contract to sweep the contract and manually give people their airdrop. Decrease scenario Cannot change vote factor after deploying contract without skewing existing votes. There is no code that currently uses voting, so this is potentially of no consequence. However, presumably the voting functionality exists for a reason, and will be used by other code. In particular, the implementation of adjust() takes care to preserve people's number of voting tokens. As the distributor contracts are not upgradeable, this means no fair elections can be run atop airdrops deployed with the current code after setVoteFactor is called.
```solidity
function setVoteFactor(uint256 _voteFactor) external onlyOwner {
    voteFactor = _voteFactor;
    emit SetVoteFactor(voteFactor);
}
```
setVoteFactor does not change supply
```solidity
function _initializeDistributionRecord(
    address beneficiary,
    uint256 totalAmount
) internal virtual override {
    super._initializeDistributionRecord(beneficiary, totalAmount);
    // add voting power through ERC20Votes extension
    _mint(beneficiary, tokensToVotes(totalAmount));
}
```
Voting tokens are minted at distribution record initialization time.
```solidity
function _executeClaim(
    address beneficiary,
    uint256 totalAmount
) internal virtual override returns (uint256 _claimed) {
    _claimed = super._executeClaim(beneficiary, totalAmount);
    // reduce voting power through ERC20Votes extension
    _burn(beneficiary, tokensToVotes(_claimed));
}
```
tokensToVotes uses the current voteFactor. If it has increased since someone's vote tokens were minted, they will not have enough tokens to burn, and so executeClaim will revert.

## Recommendation
Do not use separate voting tokens for votes; just use the amount of unclaimed token
