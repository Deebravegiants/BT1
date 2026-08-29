# [M] Rogue pool in Shelter

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-02-concur
Published: 2022-02-06
Source: https://github.com/code-423n4/2022-02-concur-findings/issues/74
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-02-concur/blob/72b5216bfeaa7c52983060ebfc56e72e0aa8e3b0/contracts/Shelter.sol#L38-L42


# Vulnerability details

## Impact
Shelter contract can steal user tokens.

## Proof of Concept
Shelter `client` can call `activate` on an already activated token, this will reset its start time, so if the client activate a token when it `GRACE_PERIOD` is almost finished, it will reset this time.
This will prevent the user to call `withdraw` because the condition `activated[_token] + GRACE_PERIOD < block.timestamp` but will allow the client to call `deactivate` and receive all funds from the users because it will satisfy the condition `activated[_token] + GRACE_PERIOD > block.timestamp`.

Steps:
- client `activate` tokenA.
- Users deposit tokenA using `donate`.
- client `activate` tokenA again until they has enough tokens.
- More users use `donate`.
- client deactivate tokenA and receive all tokens.

## Recommended Mitigation Steps
- Avoid `activate` twice for the same token
- `donate` only after the `GRACE_PERIOD`
