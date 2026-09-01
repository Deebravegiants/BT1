# [?] seeder: Fix potential UB/race condition when starting DNS threads

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2024-03-19
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/6693b7bfd4a5d64c37415b0bee50c6d8d37b458d
Type: security-commit

## Details
seeder: Fix potential UB/race condition when starting DNS threads

The DNS threads all share a static file descriptor for the listenSocket.
When starting up, the first DNS thread that is created initializes this
socket. However, no locks were being used to ensure that only 1 thread
passes through the initialization at a time.

Instead, the original author of the seeder used a Sleep(20) call to
"hope" that only 1 thread goes through there at once. This is not
guaranteed to always succeed (depending on machine load, scheduler, etc)
and was a potential source of C++ UB.

This commit fixes the situation by ensuring no such race can occur at
app startup, thus ensuring no UB.
