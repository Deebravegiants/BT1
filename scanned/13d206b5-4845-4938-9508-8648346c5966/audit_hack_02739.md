# [M] Passing the diamond facet address control

## Summary
Severity: Medium
Reporter: vlad
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultDiamond.sol#L19
Type: audit-issue

## Details
# Passing the diamond facet address control

## Summary

## Severity

Medium

## Vulnerability Detail

## Bug Description

There is `fallback` function in `VaultDiamond` contract that performs a `delegatecall` on facet address. Here is the way how the facet address is calculated:
```solidity
address implementation = address(bytes20(l.facets[msg.sig]));
```

But `msg.sig` does not have any check that the message data contains at least 4 bytes under the hood. Especially, this will fill the missing bytes with null values. So, using `msg.sig` without a check on its length leads to an incorrect key for reading from `selectorToFacetAndPosition` mapping.

So `msg.sig` will also process provided bytes and fill the rest bytes of `functionSelector` with zero value in case when `data.length` is smaller than 4.

## Attack scenario 

- Diamond proxy has one selector that ends with one zero bytes, like `0x11223300`.
- This facet has a fallback function.
- It is not expected that someone can call this fallback, since the diamond hasn't been set zero selectors is a valid one.

Then it is possible to call the diamond proxy with `0x112233` calldata, please notice that calldata size is 3 and msg.sig == `0x11223300`, it is how Solidity works. So the diamond proxy will find a facet and make a dellegatecall to the address of facet. Finally, the facet will not recognize `0x112233` as a function selector and will execute the fallback.

## Recommended Mitigation Steps

Consider adding a special check on the length of message data to enforce that it has at least 4 bytes.

## Code Snippet

- https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultDiamond.sol#L19


## Tool used

Manual Review
