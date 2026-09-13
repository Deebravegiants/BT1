# [H] There are some issues with the code

## Summary
Severity: High
Reporter: OCC
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L40
Type: audit-issue

## Details
# There are some issues with the code

## Summary
There are some issues with the code that may result in failed to running the system smoothly. 

## Vulnerability Detail
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L40
The `Alchemist` and `Migrator `interfaces are not being imported properly. It seems instead of importing ERC721 and ERC20, import the `Alchemist` and `Migrator` interfaces using from `vyper.interfaces import Alchemist, Migrator`.

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L189
I think the `NFT` variable is not being set properly. Since it is a storage variable, use `self.NFT = _nft_address` instead of `NFT = _nft_address`.

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L191
Nevermind,  `is_operator` should be initialized with `False` 

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L200
It seems the `register_deposit` function is missing the `nonpayable `modifier.

## Impact
High

## Code Snippet
Manually review

## Tool used
Manually review

### Manual Review
Done

## Recommendation
It is important to minimize errors and bugs in a system in order to ensure its security.
