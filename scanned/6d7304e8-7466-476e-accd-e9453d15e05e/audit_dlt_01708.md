# [?] notifications/tests: Fix tests to avoid overflow on adding duration to instant (#7793)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2025-03-05
Source: https://github.com/paritytech/polkadot-sdk/commit/7db67f3bff6019c6c07a2a3a380b370723fa39b1
Type: security-commit

## Details
notifications/tests: Fix tests to avoid overflow on adding duration to instant (#7793)

The tokio instant timer produced an overflow when the `poll_tick` was
called because the timer period was set to `u64::max`. The period is
reduced to accommodate for the following tokio time addition:


Source code
[tokio/time/interval.rs](https://github.com/tokio-rs/tokio/blob/a2b12bd5799f06e912b32ac05a5ffb5cf1fe31cd/tokio/src/time/interval.rs#L478-L485):
```rust
        let next = if now > timeout + Duration::from_millis(5) {
            self.missed_tick_behavior
                .next_timeout(timeout, now, self.period)
        } else {
            timeout
                .checked_add(self.period)
                .unwrap_or_else(Instant::far_future)
        };
```


Detected by:
https://github.com/paritytech/polkadot-sdk/actions/runs/13648141251/job/38150825582?pr=7790


```
──── TRY 1 STDERR:       sc-network protocol::notifications::tests::conformance::litep2p_disconnects_libp2p_substream
thread 'protocol::notifications::tests::conformance::litep2p_disconnects_libp2p_substream' panicked at std/src/time.rs:417:33:
overflow when adding duration to instant
stack backtrace:
   0: rust_begin_unwind
   1: core::panicking::panic_fmt
   2: core::option::expect_failed
   3: <std::time::Instant as core::ops::arith::Add<core::time::Duration>>::add
   4: tokio::time::interval::Interval::poll_tick
   5: sc_network::protocol::notifications::tests::conformance::litep2p_disconnects_libp2p_substream::{{closure}}
   6: tokio::runtime::scheduler::current_thread::Context::enter
   7: tokio::runtime::context::scoped::Scoped<T>::set
```

_Trimmed to 38 lines — full report: https://github.com/paritytech/polkadot-sdk/commit/7db67f3bff6019c6c07a2a3a380b370723fa39b1_
