# [C] \[C02\] Repeatedly resolve proposals

## Summary
Severity: Critical
Source: https://github.com/UMAprotocol/protocol/blob/0c4cea3c3d5e48da6f8984b8ba3afdfea4ce47cc/packages/core/contracts/oracle/implementation/Proposer.sol#L78-L81
Type: audit-issue

## Details
The `resolveProposal` function of the `Proposer` contract [simply validates](https://github.com/UMAprotocol/protocol/blob/0c4cea3c3d5e48da6f8984b8ba3afdfea4ce47cc/packages/core/contracts/oracle/implementation/Proposer.sol#L78-L81) that the oracle has resolved, but does not check if the bond has been distributed. This means the same proposal can be resolved multiple times, resulting in duplicate bond payments. Consider flagging or deleting existing proposals when they are resolved.

**Update:** _Fixed as of commit [b152718](https://github.com/UMAprotocol/protocol/pull/3689/commits/b15271849bd002fa76d109d46b4aca0cfdd3890f) in [PR3689](https://github.com/UMAprotocol/protocol/pull/3689)._


None.
