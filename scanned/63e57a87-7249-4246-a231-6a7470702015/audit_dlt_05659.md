# [?] Fix authentication bypass for direct `/v2/validator/*` endpoints (#16226)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-01-16
Source: https://github.com/OffchainLabs/prysm/commit/ce72deb3c04ee468f53a97e0b866c38fc44e62d3
Type: security-commit

## Details
Fix authentication bypass for direct `/v2/validator/*` endpoints (#16226)

This PR fixes a security vulnerability where authenticated endpoints
could be accessed without authorization by using direct
`/v2/validator/*` paths instead of `/api/v2/validator/*`.

The `AuthTokenHandler` middleware only checked for authentication on
requests containing `/api/v2/validator/` or `/eth/v1` prefixes, but the
same handlers are also registered for direct `/v2/validator/*` routes.
This allowed attackers to bypass authentication by simply removing the
`/api` prefix from the URL.

---------

Co-authored-by: james-prysm <90280386+james-prysm@users.noreply.github.com>
