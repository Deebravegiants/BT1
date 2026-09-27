# [?] CORDA-3932 Correct race condition in FlowVersioningTest (#6536)

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2020-07-31
Source: https://github.com/corda/corda/commit/68feb1c35fa37379f492803fb3bf047321883d4d
Type: security-commit

## Details
CORDA-3932 Correct race condition in FlowVersioningTest (#6536)

Correct race condition in FlowVersioningTest where the last message is read (and the session close can be triggered)
before one side has finished reading metadata from the session.
