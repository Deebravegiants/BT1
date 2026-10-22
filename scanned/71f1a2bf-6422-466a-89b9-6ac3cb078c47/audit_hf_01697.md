# [M] Users can burn protocol fees before the recipients are set

## Summary
Severity: Medium
Contest weight: 0.4307
Dataset id: 9287
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function mintVaultsInterest() external {
    uint256 interestSinceLastMint = totalAccruedDebt - lastRecordedAccruedDebt;
    require(interestSinceLastMint > 0, "No interest to mint");
    lastRecordedAccruedDebt = totalAccruedDebt; // Update the last recorded debt to the current
    uint256 remainingInterest = interestSinceLastMint;
    // Mint to configured recipients
    for (uint i = 0; i < mintRecipients.length; i++) {
        uint256 amountToMint = (interestSinceLastMint * mintRecipients[i].percentage) / 10000;
        if (amountToMint > 0) {
            IERC20(debtToken).mint(mintRecipients[i].recipient, amountToMint);
            remainingInterest -= amountToMint;
        }
    }
    // Mint any remaining amount to the default recipient
    if (remainingInterest > 0 && defaultInterestRecipient != address(0)) {
        IERC20(debtToken).mint(defaultInterestRecipient, remainingInterest);
    }
    emit VaultInterestMinted(interestSinceLastMint);
}
```
the function is external meaning that it can be called by anyone. If there is no recipients the fees will just be lost because debt token will not be minted to anyone and lastRecordedAccruedDebt will be updated. Because the recipients and the defaultInterestRecipient are not set in the constructor and must be set after by the owner, a user may call the function mintVaultsInterest and essentially not allow the interest to be claimed since the recipients have yet to be set.

## Recommendation
Set the mintVaultsInterest function to onlyOwner.
