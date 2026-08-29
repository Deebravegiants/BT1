# [?] Fix race condition on early connection failure (#1430)

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ACINQ/eclair
Published: 2020-05-19
Source: https://github.com/ACINQ/eclair/commit/c01031708dfce49dbde79f42c01f18a2a5dd324a
Type: security-commit

## Details
Fix race condition on early connection failure (#1430)

Both `Client` and `TransportHandler` were watching the connection actor,
which resulted in undeterministic behavior during termination of
`PeerConnection`.

We now always return a message when a connection fails during
authentication.

Took the opportunity to add more typing (insert
deathtoallthestring.jpg).
