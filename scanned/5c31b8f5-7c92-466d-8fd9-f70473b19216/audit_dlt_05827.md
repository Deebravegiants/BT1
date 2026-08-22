# [?] fix: test-loop: panic less on failed tests. (#14290)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2025-09-22
Source: https://github.com/near/nearcore/commit/86d5f7b29306618fe0b8c6ada602e513a13791c3
Type: security-commit

## Details
fix: test-loop: panic less on failed tests. (#14290)

When tests fail it results in panic and it's expected that in that case
test loop wouldn't be shutdown properly. Extra panic creates noise and
makes it harder to see the actual test failure so this PR avoids panic
on testloop drop when we are already panicking which makes failed test
output much easier to read.
