# [?] [actix migration] Fix telemetry actor panic. (#14217)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2025-09-09
Source: https://github.com/near/nearcore/commit/b8e75ab3f3ec1270a484708b02f32b646c7f18c8
Type: security-commit

## Details
[actix migration] Fix telemetry actor panic. (#14217)

actix::spawn is no longer compatible with the new actor runtime.
Unfortunately this one was missed. It wasn't caught by any integration
tests because I suppose no test actually wanted to export a real
telemetry data point.

For already-migrated code, there are 3 more calls to actix::spawn in
Chunk Distribution Network code. Those would also crash if the code path
is enabled, but I'll do that in a separate PR in order to make this one
merge faster.
