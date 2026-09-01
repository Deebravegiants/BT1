# [H] Arbitrary Logic Enables ERC20 Theft

## Summary
Severity: High
Chain: Smart contract
Component: 2021-08-gravitybridge
Published: 2021-08-26
Source: https://github.com/code-423n4/2021-08-gravitybridge-findings/issues/1
Type: code-finding

## Details
# Handle

ElliotFriedman


# Vulnerability details

## Severe Issue: ERC20 Token Theft Using Arbitrary Logic

There are 2 ways that this bug can be used to drain funds from the bridge. Both are catastrophic and result in total loss of funds. The 1st method is horrible, the second method is diabolical as it can extract the most possible value out of the contracts.


Method 1.

Anyone who can use arbitrary logic commands on the cosmos side can use arbitrary logic to instruct the bridge to make an arbitrary logic call to a token that the gravity bridge owns with calldata of transfer. This would allow the attacker to steal all of the ERC20 tokens locked in the gravity bridge.


Method 2.

Alternatively, an attacker could use the arbitrary logic to approve the gravity bridge’s tokens for spending by another smart contract set up specifically to drain the gravity bridge on command. Then, the attacker could set up a cosmos event listener to the gravity chain and when the attacker witnessed someone else trying to perform the same attack of stealing ERC20 tokens by either trying to use arbitrary logic to do an approval, a transfer, or a transferFrom, they would then call the smart contract on ethereum that the gravity bridge had already approved to spend all of its token and completely drain the gravity bridge of all ERC20 assets.

Issue approval calls to your malicious smart contract on ethereum using arbitrary logic. Do this across all tokens the gravity bridge holds and issue your contract infinite approval
Setup a relayer to watch for events on gravity chain listening for other users trying to perform malicious actions such as calling approve, transfer transferFrom
When the relayer detects malicious behavior from a user on cosmos, the relayer will automatically call your smart contract on ethereum which will completely drain the gravity bridge smart contract of all funds ahead of the other attacker

Impact of this finding is that once arbitrary logic is enabled on cosmos, ALL ERC20 ASSETS CAN BE STOLEN from the gravity bridge by a few simple arbitrary logic calls.

## Proof of Concept
Provide direct links to all referenced code in GitHub. Add screenshots, logs, or any other relevant proof that illustrates the concept.

The following proof of concept is for method 1. Add the following code to a file in the solidity/test folder, then run npx hardhat test solidity/test/fileName 



import chai from "chai";
import { ethers } from "hardhat";
import { solidity } from "ethereum-waffle";
 

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-08-gravitybridge-findings/issues/1_
