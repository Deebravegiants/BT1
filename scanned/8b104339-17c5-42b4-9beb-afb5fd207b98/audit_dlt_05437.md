# [?] Fixing a race condition in active_transactions.fork_replacement_tally (#4385)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2024-01-22
Source: https://github.com/nanocurrency/nano-node/commit/06d8b4e7ba20af559e1175fc91b396c417608c71
Type: security-commit

## Details
Fixing a race condition in active_transactions.fork_replacement_tally (#4385)

I did not check the unit test, just fixing the race condition I see
because the CI failed on the assert where it couldn't find the election.
The election finding needs to be inside an ASSERT_TIMELY.
