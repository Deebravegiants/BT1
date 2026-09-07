# [M] Exchange Rate can be manipulated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-05-venus
Published: 2023-05-14
Source: https://github.com/code-423n4/2023-05-venus-findings/issues/220
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-05-venus/blob/8be784ed9752b80e6f1b8b781e2e6251748d0d7e/contracts/VToken.sol#L1463
https://github.com/code-423n4/2023-05-venus/blob/8be784ed9752b80e6f1b8b781e2e6251748d0d7e/contracts/VToken.sol#L1421
https://github.com/code-423n4/2023-05-venus/blob/8be784ed9752b80e6f1b8b781e2e6251748d0d7e/contracts/VToken.sol#L756


# Vulnerability details

## Impact
A malicious user can manipulate the protocol to receive greater rewards from the `RewardsDistributor` than they should. To achieve this the attacker manipulates the `exchangeRate`.  

The attacker `mint`s into the `VToken` contract legitimately, but also `transfer`s an amount of tokens directly to the `VToken` contract. This inflates the `exchangeRate` for all subsequent users who `mint`, and has the following impact:  
1. Allows the attacker to push their leverage past the market `collateralFactor`
2. Violates the internal accounting when `borrowing` and `repaying` causing the `totalBorrows` and the sum of the individual account borrows to become out of sync, i.e. the `totalBorrows` can become `0` while their are still some loans outstanding, leading to loss of earned interest.
3. The attacker can use the leverage to repeatedly `borrow` + `mint` into the VToken in order to inflate their share of the token rewards issued by the rewards distributor.
 
This means that all subsequent `minter`s receive less `VTokens` than they should.  

The attack cost is the loss of the `transfer` into the VToken contract. But it must be noted that the attacker still received around 65-75% of the (attackTokens + mintTokens) back.

The permanent side-effect of this exploit is that the minting of `VTokens` to any subsequent users remains stunted as there is no direct mechanism to clear the excess underlying tokens from the contract. This can taint this Pool permanently.

This exploit becomes more profitable as block count accrues and more REWARD_TOKENS are issued, or - for example - if VENUS sets up greater rewards to incentivize supplying into a particular Pool; these increased rewards are a normal practice in DeFi and could be a prime target for this manipulation. 

## Proof of Concept  
In this scenario an attacker: 
1) Needs ~60 underlying tokens (supply 10 underlying, 20 direct transfer, 30 interest)
2) Gets ~5 times more rewards than other users
3) Is still able to withdraw ~50 underlying tokens from the VToken
4) ~10 tokens are now stuck in the contract, permanently tainting exchange rate

A detailed Proof of Concept illustrating the case can be found in this [gist](https://gist.github.com/lokithe5th/cda577cc1b50cb91cfe1d4b1eccecc7e).  

The gist simulates and walks through the attack using the repo's test suite as a base.
The exploit is commented throughout it's various steps. 

## Tools Used

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-05-venus-findings/issues/220_
