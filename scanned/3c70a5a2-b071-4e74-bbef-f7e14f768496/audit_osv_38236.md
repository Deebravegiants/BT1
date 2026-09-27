# [M] nimiq/core-rs-albatross: Panic in history index request handlers when a full node runs without the history index

## Summary
Severity: Medium
Advisory: CVE-2026-35468
Aliases: GHSA-xr78-2jhh-9wf9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-35468
Type: osv

## Details
nimiq/core-rs-albatross is a Rust implementation of the Nimiq Proof-of-Stake protocol based on the Albatross consensus algorithm. Prior to version 1.3.0, two peer-facing consensus request handlers assume that the history index is always available and call blockchain.history_store.history_index().unwrap() directly. That assumption is false by construction. HistoryStoreProxy::history_index() explicitly returns None for the valid HistoryStoreProxy::WithoutIndex state. when a full node is syncing or otherwise running without the history index, a remote peer can send RequestTransactionsProof or RequestTransactionReceiptsByAddress and trigger an Option::unwrap() panic on the request path. This issue has been patched in version 1.3.0.

## References
- https://github.com/nimiq/core-rs-albatross/releases/tag/v1.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35468.json
- https://github.com/nimiq/core-rs-albatross/security/advisories/GHSA-xr78-2jhh-9wf9
- https://nvd.nist.gov/vuln/detail/CVE-2026-35468
- https://github.com/nimiq/core-rs-albatross/commit/0e5c90a6c75b722f3d6091769776a4040e694dba
- https://github.com/nimiq/core-rs-albatross/pull/3667
