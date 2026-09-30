# [M] reconcile() can be called by anyone

## Summary
Severity: Medium
Contest weight: 0.4621
Dataset id: 8072
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Anyone can call reconcile() because the the checks on lock and currentSolver are done with user supplied parameters. These checks can even pass when lock == UNLOCKED or _solverLock == _UNLOCKED_UINT. Function reconcile() can set the flags _solverCalledBack and _solverFulfilled. Luckily _trySolverLock() resets these flags. Although _trySolverLock() isn't always done, as show in the issue "_releaseSolverLock() can be run without _trySolverLock()". Currently that doesn't create an issue. Function reconcile() can do several unwanted actions:
• reconcile() creates deposits out of thin air
• Flag _solverFulfilled is unreliable
After validateBalances then _solverFulfilled is not used anymore. After _settle() then deposits is not used anymore. Places where reconcile() can be called:
• Before the call to metacall() ! not an issue.
• In PreOps hook ! before validateBalances and _settle() so is an issue.
• In UserOp hook ! before validateBalances and _settle() so is an issue.
• In Solver / PreSolver ! not an issue because then it is supposed to happen.
• In AllocateValue ! before _settle() so is an issue.
• In PostOps ! before _settle() so is an issue.
• Via safeTransferETH() of _settle() ! after the relevant logic of _settle() so is no issue.
• Via safeTransferETH() of metacall() ! deposits not used ! no issue.
```solidity
function reconcile(address environment, address solverFrom,...) ... {
    // ...
    if (lock != environment) revert InvalidExecutionEnvironment(lock); // environment is user supplied
    (address currentSolver, bool calledBack, bool fulfilled) = solverLockData();
    if (solverFrom != currentSolver) revert InvalidSolverFrom(currentSolver); // solverFrom is user supplied
    // ...
    _solverLock = uint256(uint160(currentSolver)) | _solverCalledBack;
    // ...
    _solverLock = uint256(uint160(currentSolver)) | _solverCalledBack | _solverFulfilled;
}

function _trySolverLock(SolverOperation calldata solverOp) internal returns (bool valid) {
    if (_borrow(solverOp.value)) {
        _solverLock = uint256(uint160(solverOp.from)); // resets flags `_solverCalledBack` and `_solverFulfilled`
    // ...
    } else {
        // ...
    }
}
```

## Recommendation
Access to reconcile() should be restricted to specific callers and phases. Also see issues:
• Future authorization might fail because solver contract isn't solverOp.from
• Locking mechanism is complicated
