# [H] old borrowing key is used instead ofnewBorrowingKey

## Summary
Severity: High
Contest weight: 0.2125
Dataset id: 20347
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The old borrowing key credentials are deleted in _removeKeysAndClearStorage(oldBorrowing.borrower, borrowingKey, oldLoans);
see here
And a new borrowing key is created with the holdToken, saleToken, and the address of the user who wants to take over the borrowing in the _initOrUpdateBorrowing(). see here
now the old borrowing key whose credentials are already deleted is used to update the old loans in _addKeysAndLoansInfo() instead of the newBorrowingKey generated in _initOrUpdateBorrowing() see here
wrong borrowing Key is used (i.e the old borrowing key) when adding old loans to newBorrowing
Therefore the wrong borrowing key (i.e the old borrowing key) will be added as borrowing key for tokenId of old Loans in tokenIdToBorrowingKeys in _addKeysAndLoansInfo()
(i.e when the bug of update bool being false, is corrected, devs should understand :))

## Recommendation
use newBorrowingKey when calling _addKeysAndLoansInfo() instead of old borrowing key.
