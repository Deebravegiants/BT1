# [M] Admin can rug L2 Escrow tokens leading to reputation risk

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-01-livepeer
Published: 2022-01-19
Source: https://github.com/code-423n4/2022-01-livepeer-findings/issues/165
Type: code-finding

## Details
# Handle

harleythedog


# Vulnerability details

## Impact
The `L1Escrow` contract has the function `approve` that is callable by the admin to approve an arbitrary spender with an arbitrary amount (so they can steal all of the escrow's holdings if they want). Even if the admin is well intended, the contract can still be called out which would degrade the reputation of the protocol (e.g. see here: https://twitter.com/RugDocIO/status/1411732108029181960). LPT is valuable on the Ethereum mainnet, so this rug vector should be mitigated. It would be best to restrict this function's power by only allowing approvals to other trusted protocol contracts (like L1LPTGateway, which I believe uses the escrow's approval). 

NOTE: Even if the admin is under a timelock, this is still an issue, as users have to wait a whole week to withdraw from L2 -> L1 due to the dispute period.

## Proof of Concept
See the `approve` function here: https://github.com/livepeer/arbitrum-lpt-bridge/blob/ebf68d11879c2798c5ec0735411b08d0bea4f287/contracts/L1/escrow/L1Escrow.sol#L21

## Tools Used
Inspection.

## Recommended Mitigation Steps
Restrict the power of this `approve` function so that the admin isn't able to steal funds. This can be accomplished by only allowing approvals to other protocol functions (instead of arbitrary approvals).
