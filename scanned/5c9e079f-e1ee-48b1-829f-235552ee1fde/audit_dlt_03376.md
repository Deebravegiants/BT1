# [H] Join Factory Contract Replacement

## Summary
Severity: High
Chain: Smart contract
Component: 2021-05-yield
Published: 2021-06-01
Source: https://github.com/code-423n4/2021-05-yield-findings/issues/18
Type: code-finding

## Details
# Handle

0xsomeone


# Vulnerability details

## Impact

The `JoinFactory` contract is utilizing the `create2` OPCODE (via syntactic sugar) to deploy a new `Join` instance, however, no sanitization occurs on the inputs allowing contracts and thereby ownerships to be replaced at will.

## Proof of Concept

If the `createJoin` function is invoked with the same `asset`, it will replace any existing `Join` in the specified address with a new instance whose ownership will be transferred to the caller. This breaks the logical assumption that ownership of a pool should be retained and dictated by the currently-active owner of the contract.

Referenced Code: https://github.com/code-423n4/2021-05-yield/blob/main/contracts/JoinFactory.sol#L64-L75

## Tools Used

Manual Review.

## Recommended Mitigation Steps

A `require` check should be imposed prohibiting deployments of already-created `Join`s by either utilizing a `mapping` for the hashes that is set to `true` or by dynamically evaluating whether a contract already exists at the specified address via an `isContract` invocation.
