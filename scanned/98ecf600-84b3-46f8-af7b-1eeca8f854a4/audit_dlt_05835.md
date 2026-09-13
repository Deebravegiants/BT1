# [?] Catch panics from native contracts in try_call, fix #430 (#548)

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/rs-soroban-env
Published: 2022-10-28
Source: https://github.com/stellar/rs-soroban-env/commit/3a213796684769271129b89b557976b4538a904e
Type: security-commit

## Details
Catch panics from native contracts in try_call, fix #430 (#548)

* Catch panics from native contracts in try_call, fix #430

* Change all cfg(feature="testutils") into cfg(any(test, feature="testutils"))

* Make HostError escalation paths more similar between VM and non.

* Capture escalation event itself in escalated HostError

* Adjust expected debug-event counts in tests
