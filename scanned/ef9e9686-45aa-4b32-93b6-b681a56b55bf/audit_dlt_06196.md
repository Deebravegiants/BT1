# [H] Anyone can drain `HATArbitrator` via `refundExpiredSubmitClaimRequest()` with non-existing claims

## Summary
Severity: High
Chain: Smart contract
Component: HATs-Arbitration-Contracts
Published: 2023-10-27
Source: https://github.com/hats-finance/HATs-Arbitration-Contracts-0x79a618f675857b45934ca1c413fd5f409cf89735/issues/36
Type: hats-finding

## Details
**Github username:** @0xfuje
**Submission hash (on-chain):** 0x19ab4e38f9f2427b9f055d8fe3077298a36f05be8be6ee6323e26eae031c2018
**Severity:** high

**Description:**
## Impact
All user funds in `HATArbitrator` are burned forever

## Description
An attacker can repeatedly call `refundExpiredSubmitClaimRequest()` with a non-existing submit claim to drain the `HATArbitrator` contract completely. Several weaknesses and insufficient validations of `refundExpiredSubmitClaimRequest()` allow this vulnerability:
- Function can be called with non-existing `submitClaimRequest`
- If statement is bypassed with non-existing claim
- Submitter address is not verified to be non-zero
- Transfer amount is hardcoded instead of the actual amount
- Anyone can call `refundExpiredSubmitClaimRequest()`

Other factors that contribute:
- SafeERC20 will not prevent an ERC20 token from transferring to the zero address
- Majority of popular tokens allow transfer to the zero address

`contracts/HATArbitrator.sol` - [`refundExpiredSubmitClaimRequest()`](https://github.com/hats-finance/HATs-Arbitration-Contracts-0x79a618f675857b45934ca1c413fd5f409cf89735/blob/develop/contracts/HATArbitrator.sol#L477-L498)
```solidity
    function refundExpiredSubmitClaimRequest(
        bytes32 _internalClaimId
    ) external {
        SubmitClaimRequest memory submitClaimRequest = submitClaimRequests[
            _internalClaimId
        ];

        if (
            block.timestamp <=
            submitClaimRequest.submittedAt + submitClaimRequestReviewPeriod
        ) {
            revert ClaimReviewPeriodDidNotEnd();
        }

        delete submitClaimRequests[_internalClaimId];
        token.safeTransfer(
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/HATs-Arbitration-Contracts-0x79a618f675857b45934ca1c413fd5f409cf89735/issues/36_
