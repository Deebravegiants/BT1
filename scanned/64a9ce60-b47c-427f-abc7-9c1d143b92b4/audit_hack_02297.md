# [M] \[M05\] Possible zero bond

## Summary
Severity: Medium
Source: https://github.com/UMAprotocol/protocol/blob/f24ad501c8e813cf685f72217e7f13c8f3c366df/packages/core/contracts/oracle/implementation/SkinnyOptimisticOracle.sol#L176
Type: audit-issue

## Details
The `requestPrice` function of the `SkinnyOptimisticOracle` contract [uses the final fee as the bond](https://github.com/UMAprotocol/protocol/blob/f24ad501c8e813cf685f72217e7f13c8f3c366df/packages/core/contracts/oracle/implementation/SkinnyOptimisticOracle.sol#L176) if the bond is not specified. However, the `requestAndProposePriceFor` function [may use a zero bond](https://github.com/UMAprotocol/protocol/blob/f24ad501c8e813cf685f72217e7f13c8f3c366df/packages/core/contracts/oracle/implementation/SkinnyOptimisticOracle.sol#L321), which contradicts its [@notice](https://github.com/UMAprotocol/protocol/blob/f24ad501c8e813cf685f72217e7f13c8f3c366df/packages/core/contracts/oracle/implementation/SkinnyOptimisticOracle.sol#L275) and [@param](https://github.com/UMAprotocol/protocol/blob/f24ad501c8e813cf685f72217e7f13c8f3c366df/packages/core/contracts/oracle/implementation/SkinnyOptimisticOracle.sol#L286) comments. A zero bond weakens the incentive against invalid proposal or disputes.

Fortunately, the [only call to this function](https://github.com/UMAprotocol/protocol/blob/f24ad501c8e813cf685f72217e7f13c8f3c366df/packages/core/contracts/insured-bridge/BridgePool.sol#L818) in the code base sets a proposer bond. Nevertheless, consider using the final fee if the bond is not specified.

**Update:** _Fixed as of commit [daaabfc342ba1395a577159b6eb26adb20fcd232](https://github.com/UMAprotocol/protocol/pull/3534/commits/daaabfc342ba1395a577159b6eb26adb20fcd232) in [PR3534](https://github.com/UMAprotocol/protocol/pull/3534)._
