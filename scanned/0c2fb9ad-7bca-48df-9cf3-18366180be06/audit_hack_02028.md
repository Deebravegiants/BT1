# [M] 6.9 Wrong Approval To Pool

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

*While the review was ongoing Gearbox Protocol informed us about this issue independently in parallel.

In the WETHGateway.repayCreditAccountETH an approval is given to the pool:

```
_checkAllowance(pool, amount); // T: [WG-11]
```
However, this approval is wrong and should be given to the credit manager who performs the transfer
from the WETHGateway to the pool.

Code corrected:

The code has been corrected in a further commit and the allowance is now given to the CreditManager
instead of the pool in order for the credit manager to be able to transfer the tokens from the user to the
pool.
