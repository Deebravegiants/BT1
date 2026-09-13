# [M] Validations

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-10-defiprotocol
Published: 2021-10-10
Source: https://github.com/code-423n4/2021-10-defiprotocol-findings/issues/84
Type: code-finding

## Details
# Handle

pauliax


# Vulnerability details

## Impact
function setBondPercentDiv should validate that newBondPercentDiv is not 0, or bondForRebalance will experience division by zero error otherwise. If you want to allow 0 values, then bondForRebalance should accommodate for such a possibility.

function addBounty should check that amount > 0 to prevent empty bounties.

function setMinLicenseFee should validate that it is not over 100%: newMinLicenseFee <= BASE.

function mintTo should validate that 'to' is not an empty address (0x0) to prevent accidental loss of tokens.

function validateWeights should validate that token is not this basket erc20: require(_tokens[i] != address(this));

function proposeBasketLicense could validate that 'tokenName' and 'tokenSymbol' are not empty.

function function setBondPercentDiv should validate that newBondPercentDiv > 1, otherwise it may become impossible to bondBurn because then bondAmount = totalSupply and calculation of newIbRatio will produce division by zero runtime error. Of course, this value is very unlikely but still would be nice to enforce this algorithmically.

## Recommended Mitigation Steps
Consider applying suggested validations to make the protocol more robust.
