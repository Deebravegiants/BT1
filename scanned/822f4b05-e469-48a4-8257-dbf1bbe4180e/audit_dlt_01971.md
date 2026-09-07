# [?] fix: overflow in new `next_attempt_after` calculation (#5487)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2025-02-17
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/8fc28501ff0c2f0351b17707e2252102ed9d7c35
Type: security-commit

## Details
fix: overflow in new `next_attempt_after` calculation (#5487)

### Description

Due to our lack of unit testing coverage, an overflow bug caused by
https://github.com/hyperlane-xyz/hyperlane-monorepo/pull/5455 wasn't
caught. This bug happened on 7 chains on RC and took down their
submitters.

I've noticed it now on RC due to the rising prep queues
([source](https://abacusworks.grafana.net/goto/kbQcXdcNR?orgId=1)), and
also confirmed using these logs:
https://cloudlogging.app.goo.gl/zJKqhTCTPAxETTg79.

I'm not sure why but for crashed submitters, the prep queue keeps
increasing although the only logic pushing to it lives in the submitter.
Maybe's there's a future cancellation issue with `receive_task` and as a
result it's still alive
([source](https://github.com/hyperlane-xyz/hyperlane-monorepo/blob/ab2917a424534cb034400ad85836b9f833832aaf/rust/main/agents/relayer/src/msg/op_submitter.rs#L222)).
[Logs](https://cloudlogging.app.goo.gl/qEjQq5AaFPWpvrv58) show that
messages are successfully sent over [this
channel](https://github.com/hyperlane-xyz/hyperlane-monorepo/blob/ab2917a424534cb034400ad85836b9f833832aaf/rust/main/agents/relayer/src/msg/processor.rs#L306)
to the submitter (to `base` in the logs linked), and this operation
would fail if no receiving end existed.

This PR adds a unit test that would've caught the overflow, and lowers
the max backoff period from `u32::MAX` to 10 weeks into the future.

### Drive-by changes

- Refactors the logic that calculates `next_attempt` after so it can be
tested
- adds `chrono` as a relayer dependency to easily calcualte how many
seconds are in 10 weeks

### Backward compatibility

Yes

_Trimmed to 38 lines — full report: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/8fc28501ff0c2f0351b17707e2252102ed9d7c35_
