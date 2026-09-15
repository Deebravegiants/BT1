# [?] fix: weird panic on panic

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-01-09
Source: https://github.com/fedimint/fedimint/commit/a26bd701e244a59e193288faf1347515c9ff0454
Type: security-commit

## Details
fix: weird panic on panic

I can't get #7431 to work reliably, and I can't
figure out why.

But the core motivation there was that we when tests
fail and things panic, we are getting other panics
from tokio in this place, which confuses people
and make debugging harder.

The output I have:

```
thread 'tokio-runtime-worker' (1899492) panicked at library/core/src/panicking.rs:233:5:
panic in a destructor during cleanup
thread caused non-unwinding panic. aborting.
/scripts/bridge/run-remote.sh: line 31: 1899426 Aborted                 (core dumped) remote-server "$BRIDGE_DATADIR" "$@"
```

suggests that this is a double-panic, so a simpler fix
is to just not do trickery when already panicking.
