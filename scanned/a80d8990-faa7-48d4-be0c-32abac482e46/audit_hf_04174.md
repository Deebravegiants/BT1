# [C] C-01 | Defaults Forced By Removing lendingDeskLoanConﬁgs

## Summary
Severity: Critical
Contest weight: 0.2041
Dataset id: 20855
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
With the removeLendingDeskLoanConﬁg function, a lending desk owner is able to remove the lendingDeskLoanConﬁg for loans that are still active. As a result the lending owner is able to prevent ERC1155 loans from being closed as nftCollectionIsErc1155 would be false for that lending desk and collection. Consequently, the makeLoanPayment function errantly attempts to treat ERC1155 tokens as ERC721 tokens and ultimately reverts. The lending desk owner can then subsequently add the correct lendingDeskLoanConﬁg back with the setLendingDeskLoanConﬁgs function only after the loan has expired and the owner can now claim the borrower’s collateral.

## Recommendation
Do not read from the lendingDeskLoanConﬁgs mapping in the makeLoanPayment function, instead add an additional nftCollectionIsErc1155 boolean on the Loan struct and rely on that cached value to determine how to handle the transferring of collateral. Similarly, do not rely on the lendingDeskLoanConﬁgs mapping in the liquidateDefaultedLoan function, as the conﬁg may no longer be present. Instead rely on the new nftCollectionIsErc1155 boolean that will be stored on the Loan struct.
