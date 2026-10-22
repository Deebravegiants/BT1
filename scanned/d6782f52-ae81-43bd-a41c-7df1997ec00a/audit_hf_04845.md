# [M] Incorrect selector in

## Summary
Severity: Medium
Contest weight: 0.4534
Dataset id: 22740
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
FlashRolloverLoan_G5::_acceptCommitment() allows picking the SmartCommitmentForwarder, but the selector is incorrect, making it unusable for LenderCommitmentGroup_Smart. FlashRolloverLoan_G5::_acceptCommitment() accepts the commitment to SmartCommitmentForwarder if _commitmentArgs.smartCommitmentAddress != address(0). However, the selector used is acceptSmartCommitmentWithRecipient(), which does not match SmartCommitmentForwarder::acceptCommitmentWithRecipient(), DoSing the ability to rollover loans for LenderCommitmentGroup_Smart. FlashRolloverLoan_G5 will not work for LenderCommitmentGroup_Smart loans.
```solidity
FlashRolloverLoan_G5::_acceptCommitment()
function _acceptCommitment(
    address lenderCommitmentForwarder,
    address borrower,
    address principalToken,
    AcceptCommitmentArgs memory _commitmentArgs
)
    internal
    virtual
    returns (uint256 bidId_, uint256 acceptCommitmentAmount_)
{
    uint256 fundsBeforeAcceptCommitment = IERC20Upgradeable(principalToken)
        .balanceOf(address(this));
    if (_commitmentArgs.smartCommitmentAddress != address(0)) {
        .functionCall(
            abi.encodePacked(
                abi.encodeWithSelector(
                    ISmartCommitmentForwarder
                        .acceptSmartCommitmentWithRecipient
                        .selector,
                    _commitmentArgs.smartCommitmentAddress,
                    _commitmentArgs.principalAmount,
                    _commitmentArgs.collateralAmount,
                    _commitmentArgs.collateralTokenId,
                    _commitmentArgs.collateralTokenAddress,
                    address(this),
                    _commitmentArgs.interestRate,
                    _commitmentArgs.loanDuration
                ),
                borrower //cant be msg.sender because of the flash flow
            )
        );
...
```

## Recommendation
Insert the correct selector, SmartCommitmentForwarder::acceptCommitmentWithRecipient().
