# [M] Because of rounding issues, users may not be

## Summary
Severity: Medium
Contest weight: 0.5789
Dataset id: 20236
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In order for a user to withdraw their claim, they must have enough voting tokens. However, because of rounding issues, if their voting shares are granted in multiple stages, namely by the owner adjust()-ing their share upwards, they will not have enough. 1. Owner creates airdrop and grants a user a claim of 1000 tokens. The voting factor is 5, and the fractionDenominator is set to 10000. 2. User initializes their distribution record. They are minted 1000*5/10000 = 0 voting tokens. 3. Owner adjusts everyone's claim up to 1000. Each user is minted another 1000*5/10000=0 voting tokens. 4. User fully vests 5. User cannot withdraw anything because, in order to withdraw, they must burn 2000*5/10000= 1 voting token. Unless all grants and positive adjust()'s are for exact multiples of fractionDenominator, users will be prevented from withdrawing after an upwards adjustment. and 15000 for voteFactor. Since the intention is to use voteFactor's which are not multiples of fractionDenonimator, rounding issues will occur. Rounding in tokensToVotes
```solidity
function tokensToVotes(uint256 tokenAmount) private view returns (uint256) {
    return (tokenAmount * voteFactor) / fractionDenominator;
}
```
_initializeDistributionRecord and adjust() both use tokensToVotes to mint
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

## Recommendation
Base votes on share of unclaimed tokens and not on a separate token.
