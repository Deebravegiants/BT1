# [M] No way to remove token from being payable

## Summary
Severity: Medium
Contest weight: 0.0804
Dataset id: 10486
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol lets users auction off their NFTs. Users can choose the auction currency - native or some
ERC20/payable token. There is a payable token whitelist that defines the tokens that are allowed to be used
in the auctions. Whitelisted pay tokens can only be added by the admin. However, there is no functionality
that removes a payable token from being allowed. This is a must since the token may get hacked, drained, or
rugged. A good example of this is the TERRA/LUNA stablecoin collapse.

## Recommendation
Implement a function that lets the admin delist a pay token.
