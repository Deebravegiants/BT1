# [M] 6.2 Not Initialized Variables

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

On multiple occasions, some state variables are used which are never set and there are no functions that
can update them. In particular:

- In Options.exercise, ETH is sent to self.payee. However, this variable is never set.
    Hence, ETH will be sent to 0x0 address.
- In Gauge._getReward, the recipients mapping is read. However, this mapping is never
    written, thus the recipient[account] will always be 0x0. This means, that no other recipient
    than the owner of the Gauge tokens can receive the rewards.


Code corrected:

- The Options.payee is set to the owner in the constructor. In addition, set_payee function,
    restricted to the owner, was added. It can change this field.
- The Gauge.setRecipient function was added. It allows users to set the recipients mapping.
