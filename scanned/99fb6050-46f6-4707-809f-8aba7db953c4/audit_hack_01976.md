# [M] 6.31 No Slippage Protection in Multiple Contracts

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 1 Code Corrected

push and pull functions in UniV3Vault take options arguments that contain the minimum amount of
tokens for slippage protection.


push and pull functions in MellowVault take an options argument that contains the minimum amount
of LP tokens for slippage protection.

In the following cases, these options are not used:

- ERC20RootVault.deposit calls AggregateVault._push without options, which could result in
    a call to _push of one of the described
    Vault``s without slippage protection if the first ``subVault of the
    ERC20RootVault is one of the described Vault s. With the current contract setup, this is not
    possible though.
- ERC20RootVault.withdraw calls AggregateVault._pull without options, which could result
    in a call to _pull of one of the described ``Vault``s without slippage protection.
- MStrategy.manualPull calls pull of an arbitrary Vault without options, which could result in a
    call to _pull of one of the described ``Vault``s without slippage protection.
- MStrategy._rebalancePools calls pull of an arbitrary Vault without options, which could
    result in a call to _pull of one of the described ``Vault``s without slippage protection.
- MStrategy._swapToTarget calls pull of an arbitrary Vault without options, which could result
    in a call to _pull of one of the described ``Vault``s without slippage protection.

Code corrected:

A new parameter with option for slippage protection was introduced.
