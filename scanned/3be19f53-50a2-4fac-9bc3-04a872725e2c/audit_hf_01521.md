# [M] callIndex incremented twice

## Summary
Severity: Medium
Contest weight: 0.5665
Dataset id: 8039
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function _executeSolverOperation() increases callIndex. The function is also called from a loop in either _bidFindingIteration() or _bidKnownIteration(). So callIndex is incremented twice for every failed SolverOp, which doesn't seems logical.
Also see issue "_bidFindingIteration doesn't reset key.callIndex" how this is a factor in limiting the maximum solvers to 83.
```solidity
function _bidFindingIteration(/*...*/ ) /*...*/ {
    // ...
    for (uint256 i; i < j; i++) {
        (auctionWon, key) = _executeSolverOperation(/*...*/ );
        if (auctionWon) {
            // ...
            return (auctionWon, key);
        }
    }
}

function _executeSolverOperation(/*...*/ ) /*...*/ {
    // ...
    key = key.holdSolverLock(solverOp.solver); // increments callIndex
    // ...
    if (result.executionSuccessful()) {
        key.solverSuccessful = true;
        return (true, key);
        // auctionWon = true
    }
    // ...
    ++key.callIndex; // why is this done? Is within a loop
    // ...
}

function holdSolverLock(EscrowKey memory self, address nextSolver) internal pure returns (EscrowKey memory) {
    // ...
    ++self.callIndex;
    // ...
}
```

## Recommendation
Doublecheck the usefulness of incrementing callIndex. Consider removing the increment to callIndex from _executeSolverOperation().
```solidity
function _executeSolverOperation(...) ... {
    // ...
    // ++key.callIndex;
    // ...
}
```
