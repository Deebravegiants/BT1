# [?] Fix CGC backfill race condition (#8267)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2025-11-03
Source: https://github.com/sigp/lighthouse/commit/b57d046c4ad9cf60a8053c4c43ea99e4b326bc01
Type: security-commit

## Details
Fix CGC backfill race condition (#8267)

During custody backfill sync there could be an edge case where we update CGC at the same time where we are importing a batch of columns which may cause us to incorrectly overwrite values when calling `backfill_validator_custody_requirements`. To prevent this race condition, the expected cgc is now passed into this function and is used to check if the expected cgc == the current validator cgc. If the values arent equal, this probably indicates that a very recent CGC occurred so we do not prune/update values in the `epoch_validator_custody_requirements` map.


  


Co-Authored-By: Eitan Seri-Levi <eserilev@ucsc.edu>
