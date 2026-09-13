# [M] \[M01\] Callbacks to wrong address

## Summary
Severity: Medium
Source: https://github.com/UMAprotocol/protocol/blob/f24ad501c8e813cf685f72217e7f13c8f3c366df/packages/core/contracts/oracle/implementation/SkinnyOptimisticOracle.sol#L246
Type: audit-issue

## Details
The `SkinnyOptimisticOracle` invokes callback functions on the price requester, if they exist, so the requester can respond to significant state changes. However, the callback is incorrectly invoked on the price proposer instead of the price requester in [the proposePriceFor function](https://github.com/UMAprotocol/protocol/blob/f24ad501c8e813cf685f72217e7f13c8f3c366df/packages/core/contracts/oracle/implementation/SkinnyOptimisticOracle.sol#L246). This means the price requester is unable to respond to price proposals.

Fortunately, this feature is not used in the current code base. Nevertheless, consider invoking the `priceProposed` callback on the requester.

**Update:** _Fixed at commit [7bd3faeb6f3706132f77b9ba2dce192d1a151e74](https://github.com/UMAprotocol/protocol/pull/3531/commits/7bd3faeb6f3706132f77b9ba2dce192d1a151e74) in [PR3531](https://github.com/UMAprotocol/protocol/pull/3531)._
