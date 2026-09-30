# [M] PythOracle commit() function doesn't require increasing publish time

## Summary
Severity: Medium
Contest weight: 0.4350
Dataset id: 20263
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
PythOracle commitRequested() has the following check:
https://github.com/equilibria-xyz/perennial-v2/packages/perennial-oracle/contracts/pyth/PythOracle.sol#L138-L139
However, commit() doesn't have the same check. This allows malicious user to commit prices out of order, which can potentially lead to price manipulation attacks and unfair liquidation of users or loss of protocol funds. For example, the following scenario is possible: Timestamp = 100: Alice requests to open 1 ETH long position with $10 collateral Timestamp = 113: pyth price = $980 Timestamp = 114: pyth price = $990 Timestamp = 115: pyth price = $1000 Timestamp = 116: Keeper commits requested price = $1000 (with publish timestamp = 115) Timestamp = 117: Malicious user Bob commits oracle version 101 with price = $980 (publish timestamp = 113) and immediately liquidates Alice. Even though the current price is $1000, Alice is liquidated using the price which is earlier than the price when Alice position is opened, which is unfair liquidation. The other more complex scenarios are also possible for malicious Bob to liquidate itself to steal protocol funds. Unfair liquidation as described in the scenario above or possible loss of protocol funds.

## Recommendation
Add publish time check and store publish time in PythOracle.commit():
```solidity
function commit(uint256 oracleVersion, bytes calldata updateData) external payable {
    // Must be before the next requested version to commit, if it exists
    // Otherwise, try to commit it as the next request version to commit
    if (versionList.length > nextVersionIndexToCommit && oracleVersion >= versionList[nextVersionIndexToCommit]) {
        commitRequested(nextVersionIndexToCommit, updateData);
        return;
    }
    PythStructs.Price memory pythPrice = _validateAndGetPrice(oracleVersion, updateData);
    if (pythPrice.publishTime <= _lastCommittedPublishTime) revert PythOracleNonIncreasingPublishTimes();
    _lastCommittedPublishTime = pythPrice.publishTime;
```
