# [M] Hardcoded threshold does not hold true for several trending and widely used tokens

## Summary
Severity: Medium
Reporter: stopthecap
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L55
Type: audit-issue

## Details
# Hardcoded threshold does not hold true for several trending and widely used tokens

## Summary
Hardcoded threshold does not hold true for several trending and widely used tokens

## Vulnerability Detail
Currently, Unstoppable is taking the approach to hardcode the oracle heartbeat threshold to: `constant(uint256) = 24*60*60 # 24h` 
24 Hours. While this is true for most tokens in arbitrum. There are several tokens that do have a threshold much small because they are much more volatile. 

One of those cases is Pepe. Pepe currently has a 1 hour heartbeat  threshold: https://data.chain.link/arbitrum/mainnet/crypto-usd/pepe-usd

Chainlink tends to have a smaller heartbeat  threshold when a token is first added to their feeds because they usually are in a very unstable state and the prices fluctuate a lot.

Unstoppable, with the current implementation, it would accept stale prices of a non 24 hours hearbeat token for up to 23 hours. 
If this happens, there will be a huge loss of funds when the oracle is fetched.

## Impact
Unstoppable, with the current implementation, it would accept stale prices of a non 24 hours hearbeat token for up to 23 hours. 
If this happens, there will be a huge loss of funds when the oracle is fetched.


## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L55
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L580

## Tool used

Manual Review

## Recommendation
Do not hardcode the heartbeat threshold or do not support tokens that do not use the 24 hour threshold.
