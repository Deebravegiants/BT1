# [H] Improper implementation of `arbitraryCall

## Summary
Severity: High
Contest weight: 0.5828
Dataset id: 1166
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function arbitraryCall(address who, bytes memory data) public lock externallyGoverned {
    // cannot have an active incentive for the callee
    require(incentives[who] == 0, "inc");
    ...
```

When an incentiveToken is claimed after `endStream`, `incentives[who]` will be `0` for that `incentiveToken`.

If the protocol gov is malicious or compromised, they can call `arbitraryCall()` with the address of the incentiveToken as `who` and `transferFrom()` as calldata and steal all the incentiveToken in the victim’s wallet balance up to the allowance amount.

## Proof of Concept
1. Alice approved `USDC` to the streaming contract;
2. Alice called `createIncentive()` and added `1,000 USDC` of incentive;
3. After the stream is done, the stream creator called `claimIncentive()` and claimed `1,000 USDC`;

The compromised protocol gov can call `arbitraryCall()` and steal all the USDC in Alice’s wallet balance.

## Recommendation
Consider adding a mapping: `isIncentiveToken`, setting `isIncentiveToken[incentiveToken] = true` in `createIncentive()`, and `require(!isIncentiveToken[who], ...)` in `arbitraryCall()`.
