# [?] runtime/src/enclave_rpc/client: Fix panic on drop in async context

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2024-10-22
Source: https://github.com/oasisprotocol/oasis-core/commit/cd0f3bea3443d794cc3df13206c146485a64d3ea
Type: security-commit

## Details
runtime/src/enclave_rpc/client: Fix panic on drop in async context

The graceful shutdown of active sessions was removed, as they should
not be closed when the RPC client is dropped. Instead, we should
explicitly invoke the appropriate functions.
