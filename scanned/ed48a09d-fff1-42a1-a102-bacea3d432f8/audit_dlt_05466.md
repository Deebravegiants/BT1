# [?] Fix gov proposal end-of-voting-period consensus failure. (#1103)

## Summary
Severity: Unknown
Chain: Provenance
Component: provenance-io/provenance
Published: 2022-09-29
Source: https://github.com/provenance-io/provenance/commit/8806c0f17c13b94f5cb2f0f3a0cde53dc1607624
Type: security-commit

## Details
Fix gov proposal end-of-voting-period consensus failure. (#1103)

* [1099]: Add the types to the error messages when it's not a fee tx or not a fee gas meter.

* [1099]: bypass the consumeMsgFees stuff in the message service router if the gas meter isn't a fee gas meter.
