# [M] Use Of expect() In apply_chunks() Causes Node To Crash

## Summary
Severity: Medium
Contest weight: 0.1449
Dataset id: 15137
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The apply_snapshot_chunk() method in abci.rs contains a reachable expect() when decoding request.chunk, allowing peers to cause the node to crash.
Specically, the following line is problematic:
crates/consensus/authority/src/comet_bft/abci.rs
```rust
let blocks_with_senders: Vec<_> = compressor
    .decode(request.chunk.as_ref())
    .await
    .expect("Failed to deserialize and decompress block with context"); // @audit reachable by malicious peer
```
If a peer sends a malformed or malicious chunk, the decode() operation could result in an Error, causing the program to panic due to the use of expect(). This results in a denial-of-service (DoS) vulnerability, as a malicious peer could send a malformed chunk causing a client to crash.
The likelihood is rated as low as the issue will only occur during syncing. Syncing will occur when a node is either initially starting up or falls behind the head. The impact is rated as high as the panic is unrecoverable and the node will crash.

## Recommendation
Replace the use of expect() with proper error handling to gracefully handle decoding failures.
