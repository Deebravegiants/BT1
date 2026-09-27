# [M] CAP_PER_ADDRESS alone does not enforce a meaningful restriction

## Summary
Severity: Medium
Reporter: alexxander
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L161-L165
Type: audit-issue

## Details
# CAP_PER_ADDRESS alone does not enforce a meaningful restriction

## Summary
CAP_PER_ADDRESS alone does not enforce a meaningful restriction
## Vulnerability Detail
Assuming from the in-code documentation of the project - the reason behind the CAP_PER_ADDRESS restriction is to give every participant a fair chance of participating in the mint dutch auction by denying users that would otherwise try and mint a large quantity of nft-s in a single transaction. The current implementation of `mint()` introduces a reentrancy possibility where after excess eth is refunded the fallback() function of the caller could invoke pre configured "Proxy" contracts that will mint more nfts, thus, in reality a user can still mint more than CAP_PER_ADDRESS nft's in a single transation.  
## Impact
CAP_PER_ADDRESS does not improve fairness of the dutch auction
## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L161-L165
## Tool used

Manual Review

## Recommendation
Make sure the caller is a EOA by using isContract() from OZ, alternatively, implement a whitelist.
