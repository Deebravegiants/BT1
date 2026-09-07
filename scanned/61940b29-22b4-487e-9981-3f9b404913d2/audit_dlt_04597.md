# [M] Front run initializer

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/92
Type: sherlock-finding

## Details
Deivitto

medium

# Front run initializer

## Summary
The initialize function that initializes important contract state can be called by anyone.
## Vulnerability Detail
The attacker can initialize the contract before the legitimate deployer, hoping that the victim continues to use the same contract.

In the best case for the victim, they notice it and have to redeploy their contract costing gas.
## Impact

## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L60
    function initialize(address _telAddress) public payable initializer {
## Tool used

Manual Review

## Recommendation

Use the constructor to initialize non-proxied contracts.

For initializing proxy contracts deploy contracts using a factory contract that immediately calls initialize after deployment or make sure to call it immediately after deployment and verify the transaction succeeded.
