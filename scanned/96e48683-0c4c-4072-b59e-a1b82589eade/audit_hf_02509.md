# [M] Revisited Calculation of Boosted Borrow in EcoScore

## Summary
Severity: Medium
Contest weight: 0.4607
Dataset id: 13392
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Whitehole protocol has a special system called EcoScore that measures how much each user contributes to the overall ecosystem.
It is fairly meant to reward users who have high protocol loyalty. Take the GRV distribution for example, the more a user borrow/supply in the protocol, the more GRV he/she can be rewarded. While reviewing the calculation of the total borrow amount for a user in one market, we notice it counts in the NFT borrow amount of ETH even the underlying of the given market is not ETH.
In the following, we show the code snippet of the calculateEcoBoostedBorrow() routine, which is used to calculate the boosted borrow amount for the input user in the given market. It calculates the borrow amount for the user in the given market (line 415) and the NFT borrow amount of ETH for the user (line 415), which are then added together as the total borrow amount (line 417).
However, it comes to our attention that if the underlying of the given market is not ETH, the NFT borrow amount shall not be counted into the total borrow amount, because the user can borrow only ETH asset from the NFT market. Our analysis shows that it needs to count in the NFT borrow amount only when the underlying of the given market is ETH.
```solidity
function calculateEcoBoostedBorrow(
    address market,
    address user,
    uint256 userScore,
    uint256 totalScore
) external view override returns (uint256) {
    uint256 accInterestIndex = IGToken(market).getAccInterestIndex();
    uint256 defaultBorrow = IGToken(market).borrowBalanceOf(user).mul(1e18).div(accInterestIndex);
    uint256 nftBorrow = lendPoolLoan.userBorrowBalance(user).mul(1e18).div(accInterestIndex);
    uint256 boostedBorrow = defaultBorrow.add(nftBorrow);
    Constant.BoostConstant memory boostConstant = _getBoostConstant(user);
    if (userScore > 0 && totalScore > 0) { ... }
    return Math.min(boostedBorrow, defaultBorrow.mul(boostConstant.boost_max).div(100));
}
```
What is more, while reviewing the calculation of the NFT borrow amount (line 415), we notice it uses the accInterestIndex of the given market, not the NFT market. As a result, the calculated nftBorrow is wrong. Our analysis shows that it shall use the latest pending accInterestIndex in the LendPoolLoan contract to calculate the NFT borrow amount.

## Recommendation
Count in the NFT borrow amount only for ETH market, and calculate the NFT borrow amount using the accInterestIndex of the NFT market.
