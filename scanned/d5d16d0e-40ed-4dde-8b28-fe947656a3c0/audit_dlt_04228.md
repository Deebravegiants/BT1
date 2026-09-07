# [H] Owner won't be able to burn his NFTs and receive his AMM tokens back, duo to important missed check to ensure the NFTs burned were minted on this particular depositer contract.

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-isomorph
Published: 2022-12-11
Source: https://github.com/sherlock-audit/2022-11-isomorph-judging/issues/95
Type: sherlock-finding

## Details
CodingNameKiki

high

# Owner won't be able to burn his NFTs and receive his AMM tokens back, duo to important missed check to ensure the NFTs burned were minted on this particular depositer contract.

## Summary
Owner won't be able to burn his NFTs and receive his AMM tokens back, duo to important missed check to ensure the NFTs burned were minted on this particular depositer contract.

## Vulnerability Detail
Every user who calls the function `makeNewDepositor` in Templater.sol receives a new depositer contract and the ownership of it.
Every depositer contract has a different address and owner. The problem here is that the owner is the only one, who can deposit to gauge with the function `depositToGauge`, but anyone can call the functions `partialWithdrawFromGauge`, `withdrawFromGauge` and withdraw from gauge.

This actions can lead to this scenario:

Kiki the owner of the depositer contract calls the function `depositToGauge` and deposits 1000 AMM tokens, as a result a newly NFT is minted and sent to him equaled to the price of 1000  AMM tokens. 

https://github.com/sherlock-audit/2022-11-isomorph/blob/main/contracts/Velo-Deposit-Tokens/contracts/Depositor.sol#L58-L70

In the deposit function in gauge the deposited amount is added to the mapping `balanceOf[msg.sender] += amount`
As a result Kiki's depositer contract has a balance of 1000 AMM tokens now.

https://github.com/velodrome-finance/contracts/blob/de6b2a19b5174013112ad41f07cf98352bfe1f24/contracts/Gauge.sol#L463

Since anyone can withdraw from gauge, as the functions `partialWithdrawFromGauge`, `withdrawFromGauge` are public.
And there is no check to ensure the NFTId was minted on this particular depositer contract.

A user calls the function `withdrawFromGauge` burns his NFT and receives his 500 AMM tokens back.

https://github.com/sherlock-audit/2022-11-isomorph/blob/main/contracts/Velo-Deposit-Tokens/contracts/Depositor.sol#L119-L127

As a result the balance of Kiki's depositer contract will be equal to 500 AMM tokens in gauge.

https://github.com/velodrome-finance/contracts/blob/de6b2a19b5174013112ad41f07cf98352bfe1f24/contracts/Gauge.sol#L505

When Kiki decides to withdraw from gauge, he won't be able to do it as his contract's balance in gauge will be only 500 tokens and his NFT price is 1000 AMM tokens.

Outcome:

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-isomorph-judging/issues/95_
