# [H] Flag _solverFulfilled is unreliable

## Summary
Severity: High
Contest weight: 0.7688
Dataset id: 8048
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function reconcile(/*...*/ ) /*...*/ {
    // ...
    uint256 deficit = claims + withdrawals;
    uint256 surplus = deposits + maxApprovedGasSpend + msg.value;
    // ...
    if (deficit > surplus) {
        // ...
        return deficit - surplus;
    }
    // CASE: Callback verified and solver duty fulfilled
    if (!calledBack || !fulfilled) {
        _solverLock = uint256(uint160(currentSolver)) | _solverCalledBack | _solverFulfilled;
    }
    return 0;
}

function validateBalances() external view returns (bool calledBack, bool fulfilled) {
    (, calledBack, fulfilled) = solverLockData();
    if (!fulfilled) {
        uint256 _deposits = deposits;
        // Check if locked.
        if (_deposits != type(uint256).max) {
            fulfilled = deposits >= claims + withdrawals;
        }
    }
}

function solverLockData() public view returns (address currentSolver, bool calledBack, bool fulfilled) {
    uint256 solverLock = _solverLock;
    // ...
    fulfilled = solverLock & _solverFulfilled != 0;
}
```
Function reconcile() sets the flag _solverFulfilled if sufficient funds are present. Later on validateBalances() trusts this flag and doesn't do any additional checks.
However after a call reconcile() it is still possible to do _borrow() and _contribute(), which change withdrawals and deposits. This could be done in the same hook that calls reconcile().

## Recommendation
In validateBalances() always check the end balances:
```solidity
function validateBalances() external view returns (bool calledBack, bool fulfilled) {
    (, calledBack, fulfilled) = solverLockData();
    if (!fulfilled) {
        uint256 _deposits = deposits;
        // Check if locked.
        if (_deposits != type(uint256).max) {
            fulfilled = deposits >= claims + withdrawals;
        }
    }
}
```
Remove the _solverFulfilled flag from reconcile().
