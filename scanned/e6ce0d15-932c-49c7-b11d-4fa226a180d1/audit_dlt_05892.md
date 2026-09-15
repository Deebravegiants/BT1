# [?] Recover from panic in HandleTransaction to prevent peer crash (#5472)

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2026-05-06
Source: https://github.com/hyperledger/fabric/commit/6a673975ced5a050d2e63e0a2c2d78283daf5ccb
Type: security-commit

## Details
Recover from panic in HandleTransaction to prevent peer crash (#5472)

When a transaction times out during a range query, the timeout path
closes LevelDB iterators while the handler goroutine is still using
them, causing a nil pointer dereference that crashes the peer.

Add a deferred recover() in HandleTransaction to catch such panics
and return an error response instead of crashing. This is safe because
the transaction has already timed out and the resources are being freed.

The panic value is logged but not included in the response payload to
avoid violating endorsement determinism across peers. Metrics are
recorded in the recover path to match the normal code path.

Also adds regression tests that verify the panic is recovered and
an error response is sent.

Fixes #5048

Signed-off-by: Jaskirat-s7 <jaskiratsingh7812@gmail.com>
