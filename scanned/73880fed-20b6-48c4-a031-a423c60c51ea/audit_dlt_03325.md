# [M] Does the cosmos-sdk listen to only 1 gravity.sol contract address?

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-08-gravitybridge
Published: 2021-09-07
Source: https://github.com/code-423n4/2021-08-gravitybridge-findings/issues/14
Type: code-finding

## Details
# Handle

tensors


# Vulnerability details

Recently Thorchain (which uses cosmos), was hacked because the Thorchain environment
listened to emitted events from routers other than the intended one. This allowed a hacker to create a malicious router.

Within the eth_main_loop of the orchestrator, is the gravity.sol contract address a hard-coded constant, so that
this type of exploit can't occur? I wasn't able to this constant with the repo.  

## Recommended Mitigation Steps
Can the devs confirm that this sort of vulnerability doesn't occur and that the intended contract address is indeed hard-coded?
