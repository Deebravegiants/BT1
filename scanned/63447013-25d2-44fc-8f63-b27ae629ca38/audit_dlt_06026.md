# [?] fix(iota-graphql-rpc): stop panicking on failed requests in test cluster wait helpers (#12551)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-08-11
Source: https://github.com/iotaledger/iota/commit/cd0f9cff0de8694c0e540c278ad348261110e20a
Type: security-commit

## Details
fix(iota-graphql-rpc): stop panicking on failed requests in test cluster wait helpers (#12551)

# Description of change

`wait_for_graphql_checkpoint_catchup` and
`wait_for_graphql_checkpoint_pruned` in the GraphQL test cluster
unwrapped the result of every request, so a single failed request (e.g.
an empty HTTP response while the server is still starting) panicked the
whole test.

- Replace the `unwrap()` in both wait helpers with a log-and-retry after
1s, matching the polling loops they already run in.
- The overall `tokio::time::timeout` around each loop still bounds the
wait.

## Links to any relevant issues

fixes https://github.com/iotaledger/iota/issues/12252

## How the change has been tested

- `consistency/objects_pagination` e2e tests pass locally with
`--features pg_integration`.

- [x] Basic tests (linting, compilation, formatting, unit/integration
tests)
- [ ] Patch-specific tests (correctness, functionality coverage)

### Infrastructure QA (only required for crates that are maintained by
@iotaledger/infrastructure)

- [ ] Synchronization of the indexer from genesis for a network
including migration objects.
- [ ] Restart of indexer synchronization locally without resetting the
database.
- [ ] Restart of indexer synchronization on a production-like database.
- [ ] Deployment of services using Docker.
- [ ] Verification of API backward compatibility.
