# [?] Fixed a rare crash bug when process runs out of file descriptors

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2024-04-22
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/f1ce09f06394da028a6a1b1e3042a2cdd0aebc05
Type: security-commit

## Details
Fixed a rare crash bug when process runs out of file descriptors

Rarely, it would be possible for the process to run out of file
descriptors, in which case ThreadDumper -> SaveAllToDisk() would crash.

This has been addressed by checking the results of std::fopen() and not
proceeding if the returned FILE * is nullptr.
