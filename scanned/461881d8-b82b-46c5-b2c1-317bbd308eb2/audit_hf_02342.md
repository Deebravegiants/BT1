# [M] Silent overflow of `_fCashAmount`

## Summary
Severity: Medium
Contest weight: 0.0428
Dataset id: 12723
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The issue is a silent overflow that occurs when the contract’s internal minting routine receives a value for the `_fCashAmount` parameter that exceeds the capacity of a uint88 type. The `_mint` function accepts the amount as a uint256 but then down‑casts it to uint88 without any safety check. Because Solidity truncates the high‑order bits during a down‑cast, any value larger than 2^88‑1 wraps around, producing a much smaller number. This arithmetic error is the root cause: an unchecked conversion from a larger integer type to a smaller one. An attacker or a faulty client can exploit the bug by supplying an overly large `_fCashAmount` that overflows, causing the contract to mint far fewer fCash tokens than intended, or alternatively to mint an unexpectedly large amount if the overflow wraps to a high value. The impact is a distortion of accounting within the protocol – users may receive an incorrect balance, causing funds to disappear from the sender’s perspective or to be created out of thin air for the receiver. The condition under which the bug manifests is any call to the internal `_mint` function (or any external wrapper that ultimately forwards a `_fCashAmount` argument) where the supplied amount is greater than the maximum representable uint88. Both regular users and privileged roles that interact with the minting logic are affected because the protocol’s economic guarantees rely on accurate token accounting. The vulnerability was identified during a systematic Code4rena audit when the auditors examined type conversions and noticed the lack of validation for the down‑cast. It is difficult to detect in normal operation because the transaction does not revert; the contract simply records an unintended amount, and there is no emitted warning or error. From a user’s point of view, the symptoms may appear as a missing or unexpectedly low refund, a balance that seems to vanish after a deposit, or a surprising increase in token holdings after a minting operation. This class of bug belongs to the broader category of unchecked integer down‑casting or truncation errors, which violate business logic that assumes a one‑to‑one correspondence between deposited value and minted token amount. To remediate the issue, the contract should enforce a safe conversion by checking that the incoming `_fCashAmount` does not exceed `type(uint88).max` before casting, using a helper such as `_safeUint88` that reverts on overflow. This ensures the protocol’s accounting remains truthful and prevents malicious manipulation of token supplies.

## Recommendation
// Use a safe downcast function e.g. wfCashLogic::_safeUint88
    function _safeUint88(uint256 x) internal pure returns (uint88) {hil
        require(x <= uint256(type(uint88).max));
        return uint88(x);
    }

This seems reasonable and we’ll probably adopt the suggested mitigation approach.
