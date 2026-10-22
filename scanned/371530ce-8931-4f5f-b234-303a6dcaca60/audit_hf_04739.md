# [M] TOFTOptionsReceiverModule's and UsdoOptionReceiverModule's exerciseOptionsReceiver does not handle zero amount

## Summary
Severity: Medium
Contest weight: 0.5734
Dataset id: 22565
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is a valid case of zero paymentAmount in TapiocaOptionBroker's exerciseOption(). When this happens, exerciseOptionsReceiver() does not return any exercise funds remainder to the caller. Zero amount can happen due to rounding and is allowed in the logic. However, the reimbursement logic is conditioned on non-zero balance change (while it cannot be the case as the exercise reverts on all the errors, there is no possibility to just exit), so user will not be reimbursed in this case. The _options.paymentTokenAmount provided by the caller can be lost for them if exerciseOption() ended up requesting no payment due to rounding. These user provided funds can be immediately stolen by any back-running attacker, as attacker's _options.paymentTokenAmount can be less than what they need for exercise, i.e. currently anyone can freely use the funds from the contract balance to pay for their options' exercise as user provided funds aren't controlled to match with option strike payment ones. The probability of such rounding can be estimated as low, while fund freezing impact is high. Likelihood: Low + Impact: High = Severity: Medium.

## Recommendation
Consider including zero amount case in TOFTOptionsReceiverModule's and UsdoOptionReceiverModule's exerciseOptionsReceiver() functions, e.g.:
/tOFT/modules/TOFTOptionsReceiverModule.sol#L174-L180
```solidity
// Refund if less was used.
if (bBefore >= bAfter) {
    uint256 diff = bBefore - bAfter;
    if (diff < _options.paymentTokenAmount) {
        IERC20(address(this)).safeTransfer(_options.from,
        _options.paymentTokenAmount - diff);
    }
}
```
cts/usdo/modules/UsdoOptionReceiverModule.sol#L98-L104
```solidity
// Refund if less was used.
if (bBefore >= bAfter) {
    uint256 diff = bBefore - bAfter;
    if (diff < _options.paymentTokenAmount) {
        IERC20(address(this)).safeTransfer(_options.from,
        _options.paymentTokenAmount - diff);
    }
}
```
