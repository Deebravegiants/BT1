# [H] 5.1.5 TheexecuteVirtualOrdersToBlockfunction updates the oracle with the wrong block.number

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk

**Context:** CronV1Pool.sol#L

**Description:** TheexecuteVirtualOrdersToBlockis external, meaning anyone can call this function to execute
virtual orders.

The_maxBlockparameter can be lowerblock.numberwhich will make the oracle malfunction as the oracle update
function_updateOracleuses theblock.timestampand assumes that the update was called with the reserves at
the current block.

This will make the oracle update with an incorrect value when_maxBlockcan be lower thanblock.number.

**Recommendation:** Consider adding the block number as a parameter within the_updateOraclein order for this
function to not rely on the current block.

**Twamm:** Addressed in commitf324de7.


**Spearbit:** Verified.
