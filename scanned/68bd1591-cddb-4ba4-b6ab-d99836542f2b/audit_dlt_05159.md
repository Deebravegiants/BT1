# [?] Fix underflow updating NAV when old PV was not computed correctly (#815)

## Summary
Severity: Unknown
Chain: Centrifuge
Component: centrifuge/centrifuge-chain
Published: 2022-05-24
Source: https://github.com/centrifuge/centrifuge-chain/commit/c9067683a56a26207c34a685c25930d8b7d76f3c
Type: security-commit

## Details
Fix underflow updating NAV when old PV was not computed correctly (#815)

Previously, it was possible to underflow the NAV if the old PV was not
computed correctly. This "should never happen", of course.

We now clamp the value to zero if it would have underflowed.

Any incorrect old PV will still result in a potentially miscomputed
intermediate NAV until the full NAV calculation is re-done.

Fixes #737
