# [H] PeerMessageResponse::Signing May Panic On Malformed signing_session_id

## Summary
Severity: High
Contest weight: 0.2464
Dataset id: 15150
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Peers in the network can craft a malformed signing_response and call any event in the PeerMessageResponse::Signing block to trigger a panic and crash the node.
crates/consensus/authority/src/frost_task.rs
```rust
PeerMessageResponse::Signing(signing_response) => {
    let SigningResponse { response_type, signing_session_id, psbt } = signing_response;
    let signing_session_id = FixedBytes::from_slice(&signing_session_id); // @audit signing_session_id is not being validated
}
```
The signing_session_id is not validated properly before using FixedBytes::from_slice(). This function expects the input slice to be exactly 32 bytes long. However, signing_session_id is declared as Vec in the SigningResponse struct, which means it can be of any length. Thus, an attacker can use an arbitrary length of signing_session_id to cause the from_slice() function to panic.
The impact is rated as high as it allows any network packages to crash a node. The likelihood is rated as medium as this attack vector is only reachable from authorised peers.

## Recommendation
Use FixedBytes::<32>::try_from() instead of FixedBytes::from_slice() and handle the error instead of panicking.
