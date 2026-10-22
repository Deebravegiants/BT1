# [M] GLOBAL-6 | Lacking Storage Gaps

## Summary
Severity: Medium
Contest weight: 0.0895
Dataset id: 19355
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are several Component abstract contracts that intend to be parents of upgradeable contracts, however they lack an appropriate _gap storage variable. For example, the LedgerComponent contract is an abstract contract that is meant to be inherited by upgradeable contracts, however there is a ledgerAddress storage variable defined in the LedgerComponent followed by no gap variable in the event that more variables would be added to the LedgerComponent contract.

## Recommendation
Add a storage _gap variable so that storage variables may be added to the LedgerComponent contract without causing storage collisions. For more information on the _gap variable refer to the OpenZeppelin [documentation](https://docs.openzeppelin.com/contracts/3.x/upgradeable#storage_gaps).
