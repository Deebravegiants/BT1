# [H] Reentrancy during migration allows for unauthorized access in receiveFlashLoan()

## Summary
Severity: High
Contest weight: 0.9781
Dataset id: 2999
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
OriginationControllerMigrate.migrateV3Loan() has a whenBorrowerReset modifier that resets the borrower cache after the migration function completes. This is a measure to prevent external actors from initiating a flash loan with malicious data and targeting OriginationControllerMigrate.receiveFlashLoan().
```solidity
function receiveFlashLoan(
    IERC20[] calldata assets,
    uint256[] calldata amounts,
    uint256[] calldata feeAmounts,
    bytes calldata params
) external nonReentrant {
    if (msg.sender != VAULT) revert OCM_UnknownCaller(msg.sender, VAULT);
    OriginationLibrary.OperationData memory opData = abi.decode(params, (OriginationLibrary.OperationData));
    // verify this contract started the flash loan
    if (opData.borrower != borrower) revert OCM_UnknownBorrower(opData.borrower, borrower);
    // borrower must be set
    if (borrower == address(0)) revert OCM_BorrowerNotCached();
    _executeOperation(assets, amounts, feeAmounts, opData);
}
```
The problem in OriginationControllerMigrate.migrateV3Loan() is that after OriginationControllerMigrate._initiateFlashLoan() finishes execution, the flash loan cycle that starts from Balancer.flashLoan() has already concluded and the reentrancy guards are unlocked.
However, execution continues in OriginationControllerMigrate._initializeMigrationLoan(), which will make a call to LoanCore.startLoan(), which then safe mints ERC721 PromissoryNotes to the lender and borrower for the new (migrated) loan.
At this point, the borrower or lender can utilize the onERC721Received hook external call, during which they can initiate new flash loans through Balancer.flashLoan() with arbitrary data that targets OriginationControllerMigrate.receiveFlashLoan(), which won't revert since the borrower cache hasn't yet been reset by the whenBorrowerReset modifier.
The issue now is that OriginationControllerMigrate._executeOperation() can be called with arbitrary data, which can lead to impacts such as theft of funds from anyone who has approval towards OriginationControllerMigrate and abusing safeApprove() to permanently lock OriginationControllerMigrate.migrateV3Loan().
```solidity
function migrateV3Loan()
    external
    override
    whenNotPaused
    whenBorrowerReset
{
    // code ...
    // @note borrower cache gets set in _initiateFlashLoan()
    if (flashLoanTrigger) {
        _initiateFlashLoan(oldLoanId, newTerms, msg.sender, lender, amounts);
    }
    // code ...
    // borrower cache is not reset yet
    _initializeMigrationLoan(newTerms, msg.sender, lender, amounts.amountFromLender, amounts.amountToBorrower);
    // code ...
}
```

## Recommendation
An alternative fix to the one below is to add nonReentrant modifier to OriginationControllerMigrate._initiateFlashLoan(), however, the borrower cache would still remain initialized during OriginationControllerMigrate.migrateV3Loan(), even after the flash loan has been executed.
```solidity
);
// Flash loan based on principal + interest
IVault(VAULT).flashLoan(this, assets, amounts, params);
borrower = address(0);
}
/**
 * @notice Callback function for flash loan. OpData is decoded and used to
 * execute the migration.
 *
```
```solidity
*/
modifier whenBorrowerReset() {
    if (borrower != address(0)) revert OCM_BorrowerNotReset(borrower);
    _;
    borrower = address(0);
}
```
