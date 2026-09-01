# [M] Card affiliate payouts are skipped if a single card does not have an affiliate

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-06-realitycards
Published: 2021-06-16
Source: https://github.com/code-423n4/2021-06-realitycards-findings/issues/148
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details

## Vulnerability Details

The `Market.initialize` function sets the `cardAffiliateCut` to zero if a single `_cardAffiliateAddresses` is the zero address.

```solidity
for (uint256 i = 0; i < _numberOfCards; i++) {
    if (_cardAffiliateAddresses[i] == address(0)) {
        cardAffiliateCut = 0;
    }
}
```

## Impact

Even if all other cards have a valid affiliate, no affiliate cuts are paid out to these.

## Recommended Mitigation Steps

Distribute the specified `cardAffiliateCut` equally among all non-zero card affiliates.
