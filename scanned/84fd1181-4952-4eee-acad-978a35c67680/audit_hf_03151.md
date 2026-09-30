# [M] _settleDispute() does not block the proposer

## Summary
Severity: Medium
Contest weight: 0.5624
Dataset id: 17683
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
blockCaller() in _settleDispute() is supposed to block the proposer from further bonding, but since it only removes the root access from the proposer, which they don't have, it won't block it.
Oct 3rd to Oct 5th.
```solidity
function blockCaller(bytes32 sig, address who) public override callerIsRoot {
    _canCall[sig][who] = false;
    emit BlockCaller(sig, who);
}
```
/// @notice Returns if `who` can call `sig`
/// @param sig Method signature (4Byte)
/// @param who Address of who should be able to call `sig`
```solidity
function canCall(bytes32 sig, address who) public view override returns (bool) {
    return (_canCall[sig][who] || _canCall[ANY_SIG][who] || _canCall[sig][ANY_CALLER]);
}
```
OptimisticOracle.sol#L280 calls the internal function blockCaller(), removes the root access from the proposer, which the proposer should not have in the first place.
Therefore, it's essentially a no-op.
The proposer of a malicious proposal can bond again and continue to submit new proposals.

## Recommendation
Consider changing the ANY_SIG in blockCaller() to the method signature of bond().
use the bond signature.
True, we don't block for the delegate bond(address,rates) function but that will be callable only by the oracle owner(for keeper setup). Regular proposers will only have permission to call bond(rateIds) via allowProposer().
it is expected to be restricted to only the oracle owner.
