# [?] fix(tee-prover): mitigate panic on redeployments (#2764)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2024-09-02
Source: https://github.com/matter-labs/zksync-era/commit/178b38644f507c5f6d12ba862d0c699e87985dd7
Type: security-commit

## Details
fix(tee-prover): mitigate panic on redeployments (#2764)

## What ❔

We experienced `tee-prover` panic, likely due to the automatic
redeployment of the `proof-data-handler` in the `staging` environment.
We've been getting `503 Service Unavailable` errors for an extended
period when trying to reach
http://server-v2-proof-data-handler-internal.stage.matterlabs.corp/tee/proof_input,
which resulted in a panic after reaching the retry limit.

Relevant code causing the panic:

https://github.com/matter-labs/zksync-era/blob/8ed086afecfcad30bfda44fc4d29a00beea71cca/core/bin/zksync_tee_prover/src/tee_prover.rs#L201-L203

[Relevant
logs](https://grafana.matterlabs.dev/explore?schemaVersion=1&panes=%7B%223ss%22:%7B%22datasource%22:%22cduazndivuosga%22,%22queries%22:%5B%7B%22metrics%22:%5B%7B%22id%22:%221%22,%22type%22:%22logs%22%7D%5D,%22query%22:%22container_name:%5C%22zksync-tee-prover%5C%22%22,%22refId%22:%22A%22,%22datasource%22:%7B%22type%22:%22quickwit-quickwit-datasource%22,%22uid%22:%22cduazndivuosga%22%7D,%22alias%22:%22%22,%22bucketAggs%22:%5B%7B%22type%22:%22date_histogram%22,%22id%22:%222%22,%22settings%22:%7B%22interval%22:%22auto%22%7D,%22field%22:%22%22%7D%5D,%22timeField%22:%22%22%7D%5D,%22range%22:%7B%22from%22:%221724854712742%22,%22to%22:%221724855017388%22%7D%7D%7D&orgId=1).

## Why ❔

To mitigate panics on `proof-data-handler` redeployments.

## Checklist

- [x] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [ ] Tests for the changes have been added / updated.
- [ ] Documentation comments have been added / updated.
- [x] Code has been formatted via `zk fmt` and `zk lint`.
