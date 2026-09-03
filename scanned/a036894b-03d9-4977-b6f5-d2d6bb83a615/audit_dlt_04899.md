# [H] Use of arbitrary data as signature could be dangerous

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-bullvbear
Published: 2022-11-21
Source: https://github.com/sherlock-audit/2022-11-bullvbear-judging/issues/66
Type: sherlock-finding

## Details
ak1

high

# Use of arbitrary data as signature could be dangerous

## Summary

For `matchOrder`  and `buyPosition` , the signature in the form of `bytes calldata signature` is used.
Using arbitrary data like above one could lead to multiple issues as described in impact section.

## Vulnerability Detail

The arbitrary data used as signature in [matchOrder](matchOrder) and in [buyPosition](https://github.com/sherlock-audit/2022-11-bullvbear/blob/main/bvb-protocol/src/BvbProtocol.sol#L470).
This is not safest way to deal with signature based approach.

## Impact

1. Signature replay attack.

2. Signature reuse across different bull vs bear projects if it is to be launched in multiple chains.
    Because the chain ID is not included in the data, all signatures are also valid when the project is launched on a chain with another 
    chain ID. For instance, let’s say it is also launched on Polygon. An attacker can now use all of the Ethereum signatures there. 
   Because the Polygon addresses of user’s (and potentially contracts, when the nonces for creating are the same) are often identical, 
   there can be situations where the payload is meaningful on both chains.

3. Signature without domain , nonces are not safe along with the standard specified in EIP 712.
4.  Signature reuse from different Ethereum projects & phishing
     Because the signature is very generic, there might be situations where a user has already signed data with the same format for a 
     completely different Ethereum application. Furthermore, an attacker could set up a DApp that uses the same format and trick 
     someone into signing the data. Even a very security-conscious owner that has audited the contract of this DApp (that does not 
     have any vulnerabilities and is not malicious, it simply consumes signatures that happen to have the same format) might be willing 
    to sign data for this DApp, as he does not anticipate that this puts his NFT Port project in danger.

## Code Snippet

`matchorder`


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-bullvbear-judging/issues/66_
