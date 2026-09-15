# [H] The randomIndex() can be determined

## Summary
Severity: High
Chain: Smart contract
Component: 2021-04-meebits
Published: 2021-04-30
Source: https://github.com/code-423n4/2021-04-meebits-findings/issues/74
Type: code-finding

## Details
# Handle

s1m0


# Vulnerability details

## Impact
The function randomIndex() is used to choose which id to mint theoretically randomly.
The index can be computed with a smartContract by giving him through arguments the internal/private variables numTokens and nonce gotten with getStorageAt().
Note there is also a bug with the nonce which cause it to be always 0, line 325 should be nonce = nonce.add(1);

## Proof of Concept
It's a bit long to put it here, if you want a poc dm me on discord.

## Tools Used
Manual analysis

## Recommended Mitigation Steps
Correct the nonce.
If you really want a random index the only option that i'm aware is by using Chainlink VRF.
