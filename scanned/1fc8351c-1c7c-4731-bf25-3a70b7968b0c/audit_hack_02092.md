# [M] 6.4 Orders With Salt 0 Can Be Canceled

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

The filling degree of orders with salt 0 is not tracked in the matchOrders function. But the
calculateRemaining function will use the value from fills map to compute the remaining value that
needs to be filled. The cancel function effectively sets the fills map value to the UINT256_MAX
value. Users can also cancel orders with salt 0, effectively making the asset pair not longer usable with
salt 0.


Code corrected:

A check that prevents 0 salt order cancellation was added.
