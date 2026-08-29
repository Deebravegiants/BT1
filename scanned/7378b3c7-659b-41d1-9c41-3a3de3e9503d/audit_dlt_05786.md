# [?] fix: add missing err checks to prevent panic in log (#3207)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2024-06-25
Source: https://github.com/cometbft/cometbft/commit/5ec65d2813a95b2961b2cba346b6d204d57a0549
Type: security-commit

## Details
fix: add missing err checks to prevent panic in log (#3207)

add missing err checks to prevent panic in log

Closes [#3206](https://github.com/cometbft/cometbft/issues/3206)

#### PR checklist

- [ ] Tests written/updated
- [X] Changelog entry added in `.changelog` (we use
[unclog](https://github.com/informalsystems/unclog) to manage our
changelog)
- [ ] Updated relevant documentation (`docs/` or `spec/`) and code
comments
- [ ] Title follows the [Conventional
Commits](https://www.conventionalcommits.org/en/v1.0.0/) spec
