# [M] Trust Issue of Admin Keys

## Summary
Severity: Medium
Contest weight: 0.4577
Dataset id: 32
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the DCAv2 protocol, there is a privileged admin account (with the role of TIME_LOCKED_ROLE) that plays a critical role in governing and regulating the protocol-wide operations (e.g., configuring various system parameters). It also has the privilege to control or govern the flow of assets managed by this protocol. Our analysis shows that the privileged account needs to be scrutinized. In the following, we examine the privileged account and their related privileged accesses in current contracts.
```solidity
/// @inheritdoc IDCAHubConfigHandler
function setSwapFee(uint32 _swapFee) external onlyRole(TIME_LOCKED_ROLE) {
    _validateFee(_swapFee);
    swapFee = _swapFee;
    emit SwapFeeSet(_swapFee);
}

/// @inheritdoc IDCAHubConfigHandler
function setLoanFee(uint32 _loanFee) external onlyRole(TIME_LOCKED_ROLE) {
    _validateFee(_loanFee);
    loanFee = _loanFee;
    emit LoanFeeSet(_loanFee);
}

/// @inheritdoc IDCAHubConfigHandler
function setPlatformFeeRatio(uint16 _platformFeeRatio) external onlyRole(TIME_LOCKED_ROLE) {
    if (_platformFeeRatio > MAX_PLATFORM_FEE_RATIO) revert HighPlatformFeeRatio();
    platformFeeRatio = _platformFeeRatio;
    emit PlatformFeeRatioSet(_platformFeeRatio);
}
```
privileged admin account is a plain EOA account, this may be worrisome and pose counter-party risk to the protocol users. Note that a multi-sig account could greatly alleviate this concern, though it is still far from perfect. Specifically, a better approach is to eliminate the administration key concern by transferring the role to a community-governed DAO. In the meantime, a timelock-based mechanism can also be considered as mitigation. Moreover, it should be noted that if current contracts need to be deployed behind a proxy, there is a need to properly manage the proxy-admin privileges as they fall in this trust issue as well.

## Recommendation
Promptly transfer the privileged account to the intended DAO-like governance contract. All changed to privileged operations may need to be mediated with necessary timelocks. Eventually, activate the normal on-chain community-based governance life-cycle and ensure the intended trustless nature and high-quality distributed governance.
