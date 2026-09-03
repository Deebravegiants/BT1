# [?] fix(nns): avoid subtract-with-overflow in golden-state upgrade test when node provider rewards are already overdue (#10781)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2026-07-16
Source: https://github.com/dfinity/ic/commit/f26c824ddb29d118124807c7bb28ce7cd43280c1
Type: security-commit

## Details
fix(nns): avoid subtract-with-overflow in golden-state upgrade test when node provider rewards are already overdue (#10781)

&lt;!-- ccr-slack-attribution --&gt;
_Requested by **Bas van Dijk** · [Slack
thread](https://dfinity.slack.com/archives/C0BGNGQAQBT/p1784084232659689)_

## Context

Nightly CI job "Bazel Test NNS Nightly"
[failed](https://github.com/dfinity/ic/actions/runs/29384586002/job/87255099458)
on commit `89bccc50dd4b801e41e4bfd613f6048c36ad3bfb` (master) with:

```
attempt to subtract with overflow
```

at
`rs/nns/integration_tests/src/upgrade_canisters_with_golden_nns_state.rs:452`,
in `//rs/nns/integration_tests:upgrade_canisters_with_golden_nns_state`.

## Root cause

`advance_time_to_allow_for_voting_and_node_rewards` computes:

```rust
let seconds_to_node_provider_reward_distribution = before_timestamp
    + NODE_PROVIDER_REWARD_PERIOD_SECONDS
    - state_machine.get_time().as_secs_since_unix_epoch();
```

all in `u64`. `before_timestamp` is the timestamp of the most recently
distributed monthly node provider reward, read from the golden NNS state
snapshot. `state_machine.get_time()` is the state machine's current
time, which `new_state_machine_with_golden_nns_state_or_panic` sets to
the real wall-clock time via `.with_current_time()` (see
`rs/nns/test_utils/golden_nns_state/src/lib.rs`), independent of when
the golden state snapshot was actually captured on mainnet.


_Trimmed to 38 lines — full report: https://github.com/dfinity/ic/commit/f26c824ddb29d118124807c7bb28ce7cd43280c1_
