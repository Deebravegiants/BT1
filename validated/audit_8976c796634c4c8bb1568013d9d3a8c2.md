### Title
`whenNotPaused` on `RSETH.burnFrom()` Blocks `unlockQueue`, Freezing In-Flight Withdrawal Funds - (File: contracts/LRTWithdrawalManager.sol)

### Summary
`LRTWithdrawalManager.unlockQueue()` calls `RSETH.burnFrom()`, which carries a `