# [M] Multiple functions aren't payable so quotes may fail

## Summary
Severity: Medium
Contest weight: 0.0797
Dataset id: 20452
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are multiple functions that use quotes but that aren't payable. This breaks
their compatibility with some quotes. As the 0x docs state: Certain quotes require
a protocol fee, in ETH, to be attached to the swap call.
The following flows use a quote but the external/public starting function isn't
payable:
RollerPeriphery
1) redeem
Periphery
1) removeLiquidity
2) combine
3) swapPT
4) swapYT
5) issue
See summary.
Functions won't be compatible with certain quotes causing wasted gas fees or bad
rates for users

## Recommendation
Add payable to these external/public functions
