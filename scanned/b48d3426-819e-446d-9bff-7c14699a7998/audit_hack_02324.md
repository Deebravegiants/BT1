# [M] \[M08\] Unnecessary ABIEncoderV2

## Summary
Severity: Medium
Source: https://github.com/emptysetsquad/emptyset/blob/bf9753ef9cd5b17236036257f290e0d0b850a029/protocol/contracts/src/common/ProxyRoot.sol#L18
Type: audit-issue

## Details
The [ProxyRoot](https://github.com/emptysetsquad/emptyset/blob/bf9753ef9cd5b17236036257f290e0d0b850a029/protocol/contracts/src/common/ProxyRoot.sol#L18) and [Registry](https://github.com/emptysetsquad/emptyset/blob/bf9753ef9cd5b17236036257f290e0d0b850a029/protocol/contracts/src/registry/Registry.sol#L18) contracts are using the `experimental ABIEncoderV2` `pragma` directive but there is no explicit use of it in the contract.

Furthermore, the usage of the `experimental ABIEncoderV2` is discouraged in older Solidity versions since there have been important fixes for this encoder since then. The risk can be mitigated by being extra thorough on the testing process of the project at all levels. However, even with great tests there is always a chance to miss important issues that will affect the project.

Consider removing the directive from the contract files, and consider also more conservative options, or upgrading the Solidity version used to a newer version where the [ABIEncoderV2 is stable](https://docs.soliditylang.org/en/v0.8.2/layout-of-source-files.html?highlight=experimental#abiencoderv2), or rewriting the project to use the current stable encoder.

_**Update**: Fixed on [pull request 13](https://github.com/emptysetsquad/emptyset/pull/13/commits/02ac7e5c3171d2124205607b83990eb278505140). The `ProxyRoot` contract has been removed along with the usage of the `ABIEncoderV2` pragma in the `Registry` contract._
