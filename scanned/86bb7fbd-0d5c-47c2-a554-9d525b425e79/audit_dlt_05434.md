# [?] Fix race condition in test election_scheduler.no_vacancy

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2024-04-17
Source: https://github.com/nanocurrency/nano-node/commit/e2c76ca44a96586be922ef92b64a738aef08a7fd
Type: security-commit

## Details
Fix race condition in test election_scheduler.no_vacancy

Blocks send and receive are not confirmed for sure since nothing waits for
their confirmation. If they do not confirm in time, then one of the blocks
send or receive will take the only available place in the AEC and not
block2 as expected.
