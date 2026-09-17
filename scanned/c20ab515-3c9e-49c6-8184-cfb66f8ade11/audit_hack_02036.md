# [M] 6.5 Function Pool.unlockPool Reentrancy

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 1 Code Corrected

Pools are created in a locked state and need to be unlocked first. The unlockPool function first
removes the lock and then perform the mintCallback. The _initPoolStorage is called after the
callback. This is an important function that finalizes the setup of storage for the pool. This
mintCallback after unlock and before _initPoolStorage can be misused by the malicious parties,
since all pool functions will be available during the call. Attacker can potentially misconfigure or abuse
intermediate state inconsistency for its own profit. In addition, the mintCallback is usually performed to
whitelisted position managers, while in this case any contract can be called.

Code corrected:

The callback has been removed for unlocking pools. Now, funds have to be transferred to the pool before
unlocking the pool.
