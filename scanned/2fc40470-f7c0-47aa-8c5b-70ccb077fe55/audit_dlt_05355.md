# [?] fix(starfish): prevent integer overflow in get_useful_shards_authors (#8946)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2025-10-21
Source: https://github.com/iotaledger/iota/commit/aacd0e0a5674f1ccff17c574f7ab4424ae57c13f
Type: security-commit

## Details
fix(starfish): prevent integer overflow in get_useful_shards_authors (#8946)

# Description of change

This PR fixes an integer overflow panic in `get_useful_shards_authors`
that was causing test failures in CI.

### Problem

The function performs an unchecked subtraction `block_round - round`
which panics when `round > block_round`. This can occur during startup
when we've received blocks from more recent rounds while processing
older blocks to send.

### Solution

Added a guard condition to check `block_round >= round` before the
subtraction, ensuring we only consider shards from rounds that are not
in the future relative to the block being processed.

## Links to any relevant issues

Fixes #8947  

## How the change has been tested

- [x] Basic tests (linting, compilation, formatting, unit/integration
tests)
- [x] Patch-specific tests (correctness, functionality coverage)
- [ ] I have added tests that prove my fix is effective or that my
feature works
- [x] I have checked that new and existing unit tests pass locally with
my changes
