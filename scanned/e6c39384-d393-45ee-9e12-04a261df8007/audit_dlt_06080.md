# [?] fix: wrong returned gas used and handler crash in debug APIs (#276)

## Summary
Severity: Unknown
Chain: Ronin
Component: axieinfinity/ronin
Published: 2023-05-24
Source: https://github.com/axieinfinity/ronin-archive/commit/a6dd8e4a09591819fea0e6f528fe6a18481b3af0
Type: security-commit

## Details
fix: wrong returned gas used and handler crash in debug APIs (#276)

* fix: wrong returned gas used of system transaction in debug APIs

When using debug APIs, system transaction goes through ApplyMessage which
currently accounts for instrinsicGas and refund while normal flow through
Finalize/FinalizeAndAssemble does not. This commit adds an IsSystemTransaction to
evm's config, when system transaction goes through ApplyMessage, turn on this
flag so that gasUsed does not account for intrinsicGas and refund.

* eth/tracers: fix flatCallTracer crasher (#27304)

FlatCallTracer had a crasher when it was passed `onlyTopCall: true` as config.
This PR ignores config fields inherited from the normal call tracer.
