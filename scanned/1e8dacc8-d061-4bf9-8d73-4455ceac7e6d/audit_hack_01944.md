# [M] 6.3 Locked vBNT

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

In the StandardRewards contracts, users can call depositAndJoin or
depositAndJoinPermitted to deposit underlying tokens and stake the obtained pool tokens in one
single transaction. To perform such aggregation, the protocol transfers the tokens from the user to itself
and calls BancorNetwork.depositFor to get the pool tokens that will then be used for staking.

If the token being deposited is BNT, BancorNetwork will send both bnBNT and vBNT to the contract. As
there is no handling for vBNT, it will stay locked into the contract, preventing the user to ever withdraw his
BNT from the network.

Code corrected:

depositAndJoin now keeps the pool tokens, but sends vBNT back to the provider if BNT are
deposited. Additionally, a temporary function transferProviderVBNT has been added to allow
distribution of already accumulated vBNT to their owners by the contract admin.
