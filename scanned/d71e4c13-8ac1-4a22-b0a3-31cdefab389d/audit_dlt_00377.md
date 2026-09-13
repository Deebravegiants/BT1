# [?] [network] Update quinn-proto 0.11.3 -> 0.11.13 to fix DoS vulnerability (#18814)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-02-23
Source: https://github.com/aptos-labs/aptos-core/commit/6ffba7816cef6b8396f93428466e67b75ab265bc
Type: security-commit

## Details
[network] Update quinn-proto 0.11.3 -> 0.11.13 to fix DoS vulnerability (#18814)

Update quinn-proto to address a security vulnerability where calling
retry() on an unvalidated Incoming connection could cause a server panic
when subsequently calling refuse()/ignore() with duplicate initial packets,
or when accepting connections where the initial packet fails to decrypt or
exhausts connection IDs.

This vulnerability (present in quinn-proto < 0.11.9) allows denial of
service attacks against internet-facing servers.

The fix is a Cargo.lock-only change since quinn-proto is a transitive
dependency via gcloud-sdk -> reqwest 0.12.5 -> quinn -> quinn-proto.

Co-authored-by: Cursor Agent <cursoragent@cursor.com>
