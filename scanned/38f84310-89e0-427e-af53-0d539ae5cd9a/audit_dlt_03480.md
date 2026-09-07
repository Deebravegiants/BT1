# [M] Lack of chain information in the signed data leads to potential replay attacks.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-04-meebits
Published: 2021-04-30
Source: https://github.com/code-423n4/2021-04-meebits-findings/issues/66
Type: code-finding

## Details
# Handle

shw


# Vulnerability details

## Impact

The `Offer` structure, whose hash is signed by a maker, does not contain information of the current chain. Therefore, the signature is valid on all EVM-compatible chains. In the situation of a future hard fork of the Ethereum network, the valid signatures on one chain will be replayable on the other. An attacker could then launch a replay attack to steal assets from the maker without his agreement on the other chain. Notice that this attack is also possible if `Beebot` is deployed/tested on several chains (e.g., on both Ethereum Mainnet and Kovan).

## Proof of Concept

Referenced code:

[Beebots.sol#L523-L550](https://github.com/code-423n4/2021-04-redacted/blob/main/Beebots.sol#L523-L550)

## Tools Used

None

## Recommended Mitigation Steps

Add chain information, i.e., `chainId()`, to the `Offer` structure.
